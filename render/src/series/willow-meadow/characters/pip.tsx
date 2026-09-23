import React from 'react';
import {Mouth, moodFace} from '../../../kit/face';
import {ink} from '../../../kit/style';
import type {Rig, RigProps} from '../../../kit/types';

// Pip: a small young hedgehog, three-quarter view facing right. Origin: between the feet.
const FUR = '#8a5a3b';
const FUR_DARK = '#6b4129';
const FUR_TIP = '#c99a68';
const CREAM = '#f1e1c4';
const CREAM_SHADE = '#dcc49f';
const NOSE = '#c26b76';
const SCARF = '#6f8f4e';
const SCARF_DARK = '#56733b';
const HAND: [number, number] = [150, -70];

type Pose = {lift: number; lean: number; feet: [number, number][]; paws: [number, number][]; arms?: [number, number][]};
const POSES: Record<string, Pose> = {
	stand: {lift: 0, lean: 0, feet: [[-50, -4], [62, -4]], paws: [[128, -44], [92, -36]]},
	walk: {lift: 0, lean: 3, feet: [[-50, -4], [62, -4]], paws: [[128, -44], [92, -36]]},
	sit: {lift: 22, lean: -4, feet: [[92, 0], [150, 2]], paws: [[112, -40], [80, -34]]},
	kneel: {lift: 16, lean: 9, feet: [[-60, -2], [40, 0]], paws: [[176, -8], [96, -34]], arms: [[104, -40], [176, -10]]},
	reach: {lift: 0, lean: 7, feet: [[-50, -4], [62, -4]], paws: [[222, -46], [96, -34]], arms: [[104, -44], [222, -46]]},
	hold: {lift: 0, lean: 0, feet: [[-50, -4], [62, -4]], paws: [[HAND[0], HAND[1] + 6], [HAND[0] - 16, HAND[1] + 12]]},
	hug: {lift: 0, lean: 11, feet: [[-50, -4], [62, -4]], paws: [[214, -58], [190, -36]], arms: [[104, -46], [214, -58]]},
};

/** The spiky back: points alternate between an inner and an outer ellipse along an arc. */
const spines = (cx: number, cy: number, rx: number, ry: number, spike: number, from: number, to: number, n: number) => {
	const pts: string[] = [];
	for (let i = 0; i <= n * 2; i++) {
		const a = ((from + ((to - from) * i) / (n * 2)) * Math.PI) / 180;
		const out = i % 2 === 1 ? spike : 0;
		pts.push(`${(cx + Math.cos(a) * (rx + out)).toFixed(1)},${(cy - Math.sin(a) * (ry + out)).toFixed(1)}`);
	}
	return pts;
};
const BACK = spines(-10, -118, 138, 108, 26, 205, 62, 17);

const Pip: React.FC<RigProps> = ({t, stance, mood, mouth, eye, speaking}) => {
	const pose = POSES[stance] ?? POSES.stand;
	const face = moodFace(mood);
	const walking = stance === 'walk';
	const step = walking ? Math.sin(t * 7) : 0;
	const bob = walking ? -Math.abs(Math.sin(t * 7)) * 7 : 0;
	const breathe = 1 + Math.sin(t * 2.2) * 0.012;
	const headTilt = Math.sin(t * 1.3) * 1.2 + (speaking ? Math.sin(t * 7.5) * 1.6 : 0) + (face.browTilt > 12 ? 3 : 0);
	const scarfSway = Math.sin(t * 1.7) * 6 + (walking ? step * 8 : 0);
	const tuftSway = Math.sin(t * 2.4 + 1) * 5;
	const open = Math.max(0, Math.min(1, eye * face.lid));
	const O = ink(3.5);

	return (
		<g filter="url(#softEdge)">
			<ellipse cx={20} cy={4} rx={150} ry={16} fill="#3d4a2c" opacity={0.25} />
			{pose.feet.map(([x, y], i) => (
				<ellipse key={i} cx={x + (i === 0 ? step : -step) * 12} cy={y} rx={30} ry={13} fill={FUR_DARK} {...O} />
			))}
			<g transform={`translate(0 ${pose.lift + bob}) rotate(${pose.lean} 40 -20)`}>
				<g transform={`translate(0 ${(-(breathe - 1) * 120).toFixed(2)}) scale(1 ${breathe.toFixed(4)})`}>
					<ellipse cx={30} cy={-80} rx={112} ry={78} fill={CREAM_SHADE} />
					<path d={`M${BACK[0]} L${BACK.slice(1).join(' L')} C130,-190 158,-70 112,-30 C66,4 -60,6 -118,-26 C-150,-44 -152,-60 ${BACK[0]} Z`}
						fill={FUR} {...O} />
					{BACK.filter((_, i) => i % 2 === 1).map((p, i) => {
						const [x, y] = p.split(',').map(Number);
						return <line key={i} x1={x * 0.93 - 0.7} y1={y * 0.93 - 8.26} x2={x} y2={y} stroke={FUR_TIP} strokeWidth={5} strokeLinecap="round" />;
					})}
					<ellipse cx={-30} cy={-120} rx={70} ry={48} fill={FUR_DARK} opacity={0.18} />

					{/* head */}
					<g transform={`rotate(${headTilt.toFixed(2)} 105 -110)`}>
						<path d={`M52,-176 C48,-206 ${56 + tuftSway},-236 ${70 + tuftSway},-246 C${64 + tuftSway},-228 66,-204 74,-178 Z`} fill={FUR} {...O} />
						<ellipse cx={62} cy={-168} rx={17} ry={15} fill={FUR} {...O} strokeWidth={3} />
						<ellipse cx={63} cy={-167} rx={8} ry={7} fill={CREAM_SHADE} />
						<path d="M40,-150 C60,-190 130,-190 160,-150 C180,-128 205,-118 222,-104 C230,-96 226,-84 214,-80 C190,-72 170,-64 140,-62 C95,-60 50,-80 40,-110 Z"
							fill={CREAM} {...O} />
						<circle cx={225} cy={-98} r={11} fill={NOSE} {...O} strokeWidth={2.5} />
						<circle cx={222} cy={-102} r={3.5} fill="#f4c9cf" />
						<ellipse cx={138} cy={-92} rx={15} ry={9} fill="#e9a1a6" opacity={mood === 'happy' || mood === 'proud' ? 0.6 : 0.4} />
						{/* eye, lid and brow */}
						<g transform={`translate(128 -130) scale(${face.eyeScale}) translate(-128 130)`}>
							<ellipse cx={128} cy={-130} rx={16} ry={19} fill="#1d1512" />
							<circle cx={133} cy={-137} r={6} fill="#ffffff" />
							<circle cx={123} cy={-123} r={2.5} fill="#ffffff" opacity={0.8} />
							<rect x={108} y={-152} width={40} height={42 * (1 - open)} fill={CREAM} stroke={open < 0.95 ? '#3b2a20' : 'none'} strokeWidth={2} />
						</g>
						<path d="M112,-156 Q128,-164 146,-154" fill="none" stroke={FUR_DARK} strokeWidth={3.5} strokeLinecap="round"
							transform={`translate(0 ${face.browLift}) rotate(${face.browTilt} 128 -158)`} />
						{face.tear && <path d="M142,-106 q4,8 0,12 q-5,-3 0,-12 Z" fill="#a8d0ef" stroke="#6f9fc4" strokeWidth={1.5} />}
						<g transform="translate(186 -84) scale(1.55)">
							<Mouth shape={mouth} mood={mood} />
						</g>
					</g>

					{/* scarf */}
					<path d="M44,-92 C80,-70 130,-62 168,-72 L172,-48 C130,-38 78,-44 38,-66 Z" fill={SCARF} {...O} />
					{[0, 1, 2, 3, 4, 5, 6].map((i) => (
						<line key={i} x1={52 + i * 18} y1={-84 + i * 2.6} x2={50 + i * 18} y2={-62 + i * 1.6} stroke={SCARF_DARK} strokeWidth={2} opacity={0.6} />
					))}
					<g transform={`rotate(${scarfSway.toFixed(2)} 60 -62)`}>
						<path d="M52,-66 C44,-30 40,0 46,26 L72,22 C66,-2 70,-32 76,-60 Z" fill={SCARF} {...O} />
						<path d="M46,26 l4,10 M56,25 l2,11 M66,23 l3,10" stroke={SCARF_DARK} strokeWidth={3} strokeLinecap="round" />
					</g>

					{/* arms and paws */}
					{pose.arms && (() => {
						const [[ax, ay], [bx, by]] = pose.arms;
						const d = `M${ax},${ay} Q${(ax + bx) / 2},${Math.max(ay, by) + 8} ${bx},${by}`;
						return (
							<g>
								<path d={d} fill="none" stroke="#3b2a20" strokeWidth={21} strokeLinecap="round" />
								<path d={d} fill="none" stroke={CREAM_SHADE} strokeWidth={15} strokeLinecap="round" />
							</g>
						);
					})()}
					{pose.paws.map(([x, y], i) => (
						<ellipse key={i} cx={x} cy={y} rx={17 - i} ry={12 - i} fill={CREAM} {...O} strokeWidth={2.5} />
					))}
				</g>
			</g>
		</g>
	);
};

export const rig: Rig = {
	id: 'pip',
	stances: ['stand', 'walk', 'sit', 'kneel', 'reach', 'hold', 'hug'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired'],
	height: 260,
	anchors: {hand: HAND, head: [70, -246]},
	Component: Pip,
};
