import React from 'react';
import {Mouth, moodFace} from '../../../kit/face';
import {ink} from '../../../kit/style';
import type {Rig, RigProps} from '../../../kit/types';

// Old Ben: an elderly, broad-shouldered badger in a faded waistcoat and round spectacles,
// three-quarter view facing right. Origin: between the feet.
const GREY = '#8d8a86';
const GREY_DARK = '#6c6965';
const SILVER = '#c9c6c0';
const BLACK = '#2c2a28';
const WHITE = '#f2efe8';
const VEST = '#8a6a48';
const VEST_DARK = '#6e5236';
const BUTTON = '#b48a5a';
const NOSE = '#1f1d1c';
const HAND: [number, number] = [178, -150];

type Pose = {lift: number; lean: number; feet: [number, number][]; paws: [number, number][]; arms: [[number, number], [number, number]][]};
const SHOULDER: [number, number] = [96, -210];
const POSES: Record<string, Pose> = {
	stand: {lift: 0, lean: 4, feet: [[-50, -6], [60, -6]], paws: [[120, -120]], arms: [[SHOULDER, [120, -120]]]},
	walk: {lift: 0, lean: 7, feet: [[-50, -6], [60, -6]], paws: [[128, -118]], arms: [[SHOULDER, [128, -118]]]},
	sit: {lift: 40, lean: -2, feet: [[110, -2], [170, 2]], paws: [[110, -110]], arms: [[SHOULDER, [110, -110]]]},
	kneel: {lift: 34, lean: 12, feet: [[-60, -4], [50, -2]], paws: [[190, -40]], arms: [[SHOULDER, [190, -40]]]},
	reach: {lift: 0, lean: 9, feet: [[-50, -6], [60, -6]], paws: [[250, -190]], arms: [[SHOULDER, [250, -190]]]},
	hold: {lift: 0, lean: 4, feet: [[-50, -6], [60, -6]], paws: [[HAND[0], HAND[1] + 8]], arms: [[SHOULDER, [HAND[0], HAND[1] + 8]]]},
	hug: {lift: 30, lean: 16, feet: [[-60, -4], [50, -2]], paws: [[250, -200], [230, -150]],
		arms: [[SHOULDER, [250, -200]], [[80, -180], [230, -150]]]},
};

const Ben: React.FC<RigProps> = ({t, stance, mood, mouth, eye, speaking}) => {
	const pose = POSES[stance] ?? POSES.stand;
	const face = moodFace(mood);
	const walking = stance === 'walk';
	const step = walking ? Math.sin(t * 5) : 0;
	const bob = walking ? -Math.abs(Math.sin(t * 5)) * 6 : 0;
	const breathe = 1 + Math.sin(t * 1.8) * 0.01;
	const headTilt = Math.sin(t * 1.1) * 1 + (speaking ? Math.sin(t * 6.5) * 1.8 : 0);
	const open = Math.max(0, Math.min(1, eye * face.lid));
	const O = ink(3.5);

	return (
		<g filter="url(#softEdge)">
			<ellipse cx={20} cy={4} rx={170} ry={18} fill="#3d4a2c" opacity={0.25} />
			{pose.feet.map(([x, y], i) => (
				<ellipse key={i} cx={x + (i === 0 ? step : -step) * 14} cy={y} rx={38} ry={16} fill={BLACK} {...O} />
			))}
			<g transform={`translate(0 ${pose.lift + bob}) rotate(${pose.lean} 20 -20)`}>
				<g transform={`translate(0 ${(-(breathe - 1) * 180).toFixed(2)}) scale(1 ${breathe.toFixed(4)})`}>
					{/* back arm (hug only) */}
					{pose.arms.slice(1).map(([a, b], i) => (
						<path key={`ba${i}`} d={`M${a[0]},${a[1]} Q${(a[0] + b[0]) / 2},${Math.min(a[1], b[1]) - 20} ${b[0]},${b[1]}`}
							fill="none" stroke={GREY_DARK} strokeWidth={30} strokeLinecap="round" />
					))}
					{/* body */}
					<path d="M-110,-24 C-150,-100 -120,-200 -60,-240 C-10,-272 70,-270 110,-236 C150,-196 158,-110 138,-50 C122,-10 70,4 10,4 C-50,4 -92,-4 -110,-24 Z"
						fill={GREY} {...O} />
					<path d="M-96,-120 C-86,-190 -50,-226 -4,-238" fill="none" stroke={SILVER} strokeWidth={6} strokeLinecap="round" opacity={0.7} />
					{/* waistcoat */}
					<path d="M-30,-236 C20,-262 90,-258 118,-226 C150,-190 154,-120 142,-66 L112,-30 L92,-58 L60,-26 C10,-40 -30,-90 -40,-150 C-44,-190 -40,-220 -30,-236 Z"
						fill={VEST} {...O} />
					<path d="M60,-250 L100,-170 L128,-236 C110,-254 84,-258 60,-250 Z" fill="#d9d4cb" {...O} strokeWidth={2.5} />
					<path d="M100,-170 C104,-120 104,-80 92,-58" fill="none" stroke={VEST_DARK} strokeWidth={3} />
					<path d="M-20,-200 C-10,-150 10,-100 40,-60" fill="none" stroke={VEST_DARK} strokeWidth={2.5} opacity={0.6} />
					<circle cx={108} cy={-140} r={8} fill={BUTTON} {...O} strokeWidth={2.5} />
					<circle cx={106} cy={-96} r={8} fill={BUTTON} {...O} strokeWidth={2.5} />

					{/* head */}
					<g transform={`rotate(${headTilt.toFixed(2)} 90 -250) translate(90 -250) scale(1.3) translate(-70 272)`}>
						<ellipse cx={30} cy={-318} rx={20} ry={17} fill={BLACK} {...O} strokeWidth={3} />
						<ellipse cx={31} cy={-318} rx={9} ry={7} fill={WHITE} />
						<path d="M10,-300 C20,-350 90,-372 150,-352 C190,-338 228,-312 250,-290 C262,-278 256,-262 240,-258 C200,-248 150,-244 100,-248 C50,-252 10,-265 10,-300 Z"
							fill={WHITE} {...O} />
						{/* the black stripes, silver streaked */}
						<path d="M40,-340 C80,-356 130,-350 190,-318 C196,-312 192,-304 184,-306 C140,-322 100,-328 60,-316 C44,-312 30,-330 40,-340 Z" fill={BLACK} />
						<path d="M46,-336 C80,-346 110,-344 150,-330" fill="none" stroke={SILVER} strokeWidth={3} opacity={0.8} />
						<path d="M30,-280 C50,-270 80,-266 110,-266" fill="none" stroke={GREY} strokeWidth={10} strokeLinecap="round" opacity={0.6} />
						<circle cx={250} cy={-282} r={12} fill={NOSE} {...O} strokeWidth={2} />
						<circle cx={247} cy={-286} r={3.5} fill="#6d6a68" />
						{/* eye inside the stripe */}
						<g transform={`translate(160 -318) scale(${face.eyeScale}) translate(-160 318)`}>
							<ellipse cx={160} cy={-318} rx={9} ry={11} fill="#120f0d" />
							<circle cx={163} cy={-322} r={3.4} fill="#ffffff" />
							<rect x={148} y={-331} width={24} height={26 * (1 - open)} fill={BLACK} />
						</g>
						<path d="M146,-338 Q160,-346 176,-336" fill="none" stroke={SILVER} strokeWidth={4} strokeLinecap="round"
							transform={`translate(0 ${face.browLift}) rotate(${face.browTilt} 160 -338)`} />
						{face.tear && <path d="M172,-300 q4,8 0,12 q-5,-3 0,-12 Z" fill="#a8d0ef" stroke="#6f9fc4" strokeWidth={1.5} />}
						{/* spectacles, perched low on the snout */}
						<circle cx={196} cy={-300} r={20} fill="#ffffff" fillOpacity={0.12} stroke="#6b5438" strokeWidth={3.5} />
						<path d="M176,-304 C160,-310 140,-312 120,-310" fill="none" stroke="#6b5438" strokeWidth={3} />
						<g transform="translate(222 -266) scale(1.25)">
							<Mouth shape={mouth} mood={mood} />
						</g>
					</g>

					{/* front arm and paws */}
					{pose.arms.slice(0, 1).map(([a, b], i) => (
						<g key={`fa${i}`}>
							<path d={`M${a[0]},${a[1]} Q${(a[0] + b[0]) / 2 + 10},${Math.min(a[1], b[1]) - 16} ${b[0]},${b[1]}`}
								fill="none" stroke={BLACK} strokeWidth={37} strokeLinecap="round" />
							<path d={`M${a[0]},${a[1]} Q${(a[0] + b[0]) / 2 + 10},${Math.min(a[1], b[1]) - 16} ${b[0]},${b[1]}`}
								fill="none" stroke={GREY_DARK} strokeWidth={30} strokeLinecap="round" />
						</g>
					))}
					{pose.paws.map(([x, y], i) => (
						<ellipse key={i} cx={x} cy={y} rx={20} ry={15} fill={BLACK} {...O} strokeWidth={2.5} />
					))}
				</g>
			</g>
		</g>
	);
};

export const rig: Rig = {
	id: 'ben',
	stances: ['stand', 'walk', 'sit', 'kneel', 'reach', 'hold', 'hug'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired'],
	height: 380,
	anchors: {hand: HAND, head: [100, -372]},
	Component: Ben,
};
