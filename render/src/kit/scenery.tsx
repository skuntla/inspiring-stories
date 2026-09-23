import React from 'react';
import {ink, rand} from './style';

// Reusable scenery pieces for locations. All deterministic (seeded) and drawn with the shared ink.

/** A band of rolling hills across the scene, drawn from x = -200 to 2120. */
export const Hills: React.FC<{y: number; amp: number; color: string; seed: number; outline?: number; waves?: number}> = ({
	y, amp, color, seed, outline = 0.35, waves = 4,
}) => {
	const pts: string[] = [];
	for (let i = 0; i <= waves; i++) {
		const x = -200 + (2320 * i) / waves;
		const cx = x + 2320 / waves / 2;
		pts.push(`${i === 0 ? 'M' : ''}${x},${y - rand(i, seed) * amp} ${i < waves ? `Q${cx},${y - amp - rand(i, seed + 1) * amp}` : ''}`);
	}
	return <path d={`${pts.join(' ')} L2120,1300 L-200,1300 Z`} fill={color} {...ink(3, outline)} />;
};

/** Grass blades along a ground line. */
export const Grass: React.FC<{y: number; count: number; height: number; color: string; seed: number; sway?: number; x0?: number; x1?: number}> = ({
	y, count, height, color, seed, sway = 0, x0 = -200, x1 = 2120,
}) => (
	<g>
		{Array.from({length: count}).map((_, i) => {
			const x = x0 + rand(i, seed) * (x1 - x0);
			const h = height * (0.6 + rand(i, seed + 1) * 0.7);
			const lean = (rand(i, seed + 2) - 0.5) * 30 + sway;
			return (
				<path key={i} d={`M${x},${y} Q${x + lean * 0.4},${y - h * 0.6} ${x + lean},${y - h} Q${x + lean * 0.3 + 6},${y - h * 0.55} ${x + 9},${y}`}
					fill={color} />
			);
		})}
	</g>
);

/** Small flowers scattered over a band. */
export const Flowers: React.FC<{y0: number; y1: number; count: number; color: string; seed: number}> = ({y0, y1, count, color, seed}) => (
	<g>
		{Array.from({length: count}).map((_, i) => (
			<circle key={i} cx={-100 + rand(i, seed) * 2120} cy={y0 + rand(i, seed + 1) * (y1 - y0)} r={5 + rand(i, seed + 2) * 4}
				fill={color} opacity={0.85} />
		))}
	</g>
);

/** A crooked wooden fence from (x0, y0) to (x1, y1). */
export const Fence: React.FC<{x0: number; y0: number; x1: number; y1: number; posts: number; seed: number; color?: string}> = ({
	x0, y0, x1, y1, posts, seed, color = '#8a7358',
}) => (
	<g>
		{Array.from({length: posts}).map((_, i) => {
			const f = i / Math.max(1, posts - 1);
			const x = x0 + (x1 - x0) * f;
			const y = y0 + (y1 - y0) * f;
			const tilt = (rand(i, seed) - 0.5) * 8;
			return <rect key={i} x={x - 10} y={y - 140} width={20} height={150} rx={4} fill={color} {...ink(2.5)} transform={`rotate(${tilt} ${x} ${y})`} />;
		})}
		<path d={`M${x0 - 10},${y0 - 100} L${x1 + 10},${y1 - 100}`} stroke="#7a6349" strokeWidth={14} strokeLinecap="round" />
		<path d={`M${x0 - 10},${y0 - 52} L${x1 + 10},${y1 - 52}`} stroke="#7a6349" strokeWidth={12} strokeLinecap="round" />
	</g>
);

/** A rounded leafy tree (oak-like). */
export const Tree: React.FC<{x: number; y: number; scale: number; leaf: string; trunk: string; outline?: number}> = ({
	x, y, scale, leaf, trunk, outline = 0.6,
}) => (
	<g transform={`translate(${x} ${y}) scale(${scale})`}>
		<path d="M-18,0 C-14,-60 -22,-110 -10,-150 L12,-150 C22,-110 16,-60 20,0 Z" fill={trunk} {...ink(3, outline)} />
		<ellipse cx={0} cy={-200} rx={120} ry={80} fill={leaf} {...ink(3, outline)} />
		<ellipse cx={-70} cy={-160} rx={70} ry={50} fill={leaf} {...ink(3, outline)} />
		<ellipse cx={75} cy={-162} rx={75} ry={52} fill={leaf} {...ink(3, outline)} />
	</g>
);

/** A weeping willow: dome and drooping strands that sway. */
export const Willow: React.FC<{x: number; y: number; scale: number; t: number}> = ({x, y, scale, t}) => (
	<g transform={`translate(${x} ${y}) scale(${scale})`}>
		<path d="M4,0 C8,-70 0,-130 14,-186 L28,-186 C32,-120 24,-60 32,0 Z" fill="#6e5a44" {...ink(3, 0.7)} />
		<path d="M-110,-150 C-120,-230 -20,-260 20,-256 C80,-260 150,-220 140,-150 C90,-170 -60,-170 -110,-150 Z" fill="#88a262" {...ink(3, 0.7)} />
		{Array.from({length: 17}).map((_, i) => {
			const sx = -104 + i * 15;
			const len = 110 + Math.sin(i * 1.7) * 30 + (i > 3 && i < 13 ? 40 : 0);
			const s = Math.sin(t * 1.1 + i * 0.7) * 6;
			return (
				<path key={i} d={`M${sx},${-168 + Math.abs(i - 8) * 1.5} C${sx - 6},-130 ${sx - 10 + s},${len * 0.7 - 190} ${sx - 8 + s * 1.4},${len - 190}`}
					fill="none" stroke={i % 2 ? '#7f9a5c' : '#93ae6c'} strokeWidth={7} strokeLinecap="round" />
			);
		})}
	</g>
);

/** A low rounded stone, optionally mossy. */
export const Stone: React.FC<{x: number; y: number; w: number; h: number; moss?: boolean}> = ({x, y, w, h, moss}) => (
	<g transform={`translate(${x} ${y})`}>
		<path d={`M${-w / 2},0 C${-w / 2},${-h * 0.9} ${-w / 4},${-h} 0,${-h} C${w / 4},${-h} ${w / 2},${-h * 0.8} ${w / 2},0 Z`} fill="#9a9a92" {...ink(3)} />
		{moss && <path d={`M${-w / 2.4},${-h * 0.6} C${-w / 4},${-h * 1.05} ${w / 4},${-h * 1.05} ${w / 2.3},${-h * 0.55} C${w / 5},${-h * 0.75} ${-w / 5},${-h * 0.75} ${-w / 2.4},${-h * 0.6} Z`} fill="#6f8f45" {...ink(2)} />}
	</g>
);

/** A clump of wild mint leaves. */
export const Mint: React.FC<{x: number; y: number; scale?: number; seed: number}> = ({x, y, scale = 1, seed}) => (
	<g transform={`translate(${x} ${y}) scale(${scale})`}>
		{Array.from({length: 9}).map((_, i) => {
			const a = -80 + rand(i, seed) * 160;
			const h = 40 + rand(i, seed + 1) * 40;
			return (
				<g key={i} transform={`rotate(${a * 0.5})`}>
					<path d={`M0,0 L0,${-h}`} stroke="#4f7a3a" strokeWidth={3} />
					<path d={`M0,${-h} C12,${-h - 8} 14,${-h - 22} 0,${-h - 26} C-14,${-h - 22} -12,${-h - 8} 0,${-h} Z`} fill="#7cba5a" {...ink(1.8)} />
				</g>
			);
		})}
	</g>
);
