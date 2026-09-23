import React from 'react';
import {BEAK_OPEN, moodFace} from '../../../kit/face';
import {ink} from '../../../kit/style';
import type {Rig, RigProps} from '../../../kit/types';

// Wren: a tiny, quick brown wren with a speckled chest, an upturned tail, a pale eyebrow stripe
// and a red berry tucked behind one wing. Facing right. Origin: at the feet.
const BROWN = '#8b6440';
const BROWN_DARK = '#6a4a2c';
const CHEST = '#e3cfa8';
const SPECKLE = '#9a7550';
const BEAK = '#e0a54a';
const BERRY = '#c8323a';

const Wren: React.FC<RigProps> = ({t, stance, mood, mouth, eye, speaking}) => {
	const face = moodFace(mood);
	const flying = stance === 'fly';
	const hop = speaking ? Math.abs(Math.sin(t * 9)) * 3 : 0;
	// perched: standing on a stone or rail about 58 px tall; flying: hovering well above the ground
	const lift = flying ? -120 + Math.sin(t * 3) * 10 : stance === 'perch' ? -58 : 0;
	const flap = flying ? Math.sin(t * 22) * 50 : Math.sin(t * 1.5) * 3;
	const tailFlick = Math.sin(t * 2.3) * 6 + (speaking ? Math.sin(t * 11) * 6 : 0);
	const beak = BEAK_OPEN[mouth] * 10;
	const open = Math.max(0, Math.min(1, eye * face.lid));
	const O = ink(3);

	return (
		<g filter="url(#softEdge)">
			{stance === 'stand' && <ellipse cx={0} cy={3} rx={46} ry={7} fill="#3d4a2c" opacity={0.25} />}
			{!flying && (
				<g stroke={BROWN_DARK} strokeWidth={4} strokeLinecap="round" transform={`translate(0 ${lift})`}>
					<path d="M-8,-26 L-12,0 M-12,0 L-22,2 M-12,0 L-4,2" fill="none" />
					<path d="M10,-26 L10,0 M10,0 L0,2 M10,0 L18,2" fill="none" />
				</g>
			)}
			<g transform={`translate(0 ${lift - hop})`}>
				{/* upturned tail */}
				<path d="M-40,-60 L-78,-118 L-62,-122 L-30,-72 Z" fill={BROWN_DARK} {...O} transform={`rotate(${tailFlick} -36 -64)`} />
				{/* body */}
				<ellipse cx={0} cy={-62} rx={48} ry={40} fill={BROWN} {...O} />
				<path d="M8,-30 C30,-34 44,-50 44,-66 C38,-44 22,-34 8,-30 Z" fill={CHEST} />
				<ellipse cx={20} cy={-54} rx={24} ry={22} fill={CHEST} {...O} strokeWidth={2} />
				{[[14, -62], [24, -52], [12, -46], [28, -64], [20, -40]].map(([x, y], i) => (
					<circle key={i} cx={x} cy={y} r={2.4} fill={SPECKLE} />
				))}
				{/* wing (flaps when flying) with the berry badge */}
				<g transform={`rotate(${-flap} -6 -74)`}>
					<path d="M-6,-74 C-40,-80 -52,-50 -40,-40 C-20,-44 -6,-56 -6,-74 Z" fill={BROWN_DARK} {...O} />
					<path d="M-34,-58 L-18,-62 M-36,-50 L-20,-54" stroke={BROWN} strokeWidth={2} />
				</g>
				<circle cx={-4} cy={-84} r={7} fill={BERRY} {...O} strokeWidth={2} />
				<circle cx={-6} cy={-86} r={2} fill="#f28b90" />
				{/* head */}
				<circle cx={30} cy={-98} r={26} fill={BROWN} {...O} />
				<path d="M20,-114 C32,-120 46,-116 54,-106" fill="none" stroke="#efe2c4" strokeWidth={4} strokeLinecap="round"
					transform={`translate(0 ${face.browLift * 0.6}) rotate(${face.browTilt * 0.6} 38 -112)`} />
				<g transform={`translate(40 -100) scale(${face.eyeScale}) translate(-40 100)`}>
					<circle cx={40} cy={-100} r={6.5} fill="#15100c" />
					<circle cx={42} cy={-102} r={2.2} fill="#ffffff" />
					<rect x={32} y={-108} width={16} height={16 * (1 - open)} fill={BROWN} />
				</g>
				{face.tear && <path d="M44,-90 q3,6 0,9 q-4,-2 0,-9 Z" fill="#a8d0ef" stroke="#6f9fc4" strokeWidth={1.2} />}
				{/* beak: upper and lower halves part with the visemes */}
				<path d={`M52,-100 L76,${-96 - beak * 0.3} L54,-92 Z`} fill={BEAK} {...O} strokeWidth={2} />
				<path d={`M54,-92 L72,${-90 + beak} L52,-88 Z`} fill="#c98a34" {...O} strokeWidth={2} />
			</g>
		</g>
	);
};

export const rig: Rig = {
	id: 'wren',
	stances: ['stand', 'perch', 'fly'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 150,
	anchors: {hand: [0, -70], head: [30, -124]},
	Component: Wren,
};
