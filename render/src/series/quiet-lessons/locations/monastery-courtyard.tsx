import React from 'react';
import {Grass} from '../../../kit/scenery';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// The stone courtyard of an old mountain monastery above a valley: snowy peaks, the monastery hall
// with a tiered roof, prayer flags, a pine, a cloth flag on a pole that shows the wind, a stone bench
// (seated characters at left or center_left sit on it) and a small red target far across.

/** Wind strength 0..1 over time: a steady breeze with slow gusts. The flags and the pine follow it. */
export const wind = (t: number) => 0.55 + 0.25 * Math.sin(t * 0.63) + 0.2 * Math.max(0, Math.sin(t * 1.7 + 1)) ** 3;

const BENCH = [260, 1010]; // x span; seat top at y 750 (a seated rig's seat drop)
const FLAG_X = 1440;
const TARGET: [number, number] = [1760, 640];

const Peaks: React.FC<{y: number; amp: number; color: string; snow?: string; seed: number}> = ({y, amp, color, snow, seed}) => {
	const pts: [number, number][] = [];
	for (let i = 0, x = -240; x <= 2160; i++, x += 130 + rand(i, seed) * 110) pts.push([x, y - (i % 2 ? amp * (0.55 + rand(i, seed + 1) * 0.45) : amp * 0.15 * rand(i, seed + 2))]);
	const d = `M-240,${y + 400} ` + pts.map(([x, py]) => `L${x.toFixed(0)},${py.toFixed(0)}`).join(' ') + ` L2160,${y + 400} Z`;
	return (
		<g>
			<path d={d} fill={color} />
			{snow &&
				pts.map(([x, py], i) =>
					i % 2 && py < y - amp * 0.6 ? (
						<path key={i} d={`M${x - 46},${py + 52} L${x},${py} L${x + 46},${py + 52} L${x + 20},${py + 40} L${x},${py + 56} L${x - 18},${py + 42} Z`} fill={snow} />
					) : null,
				)}
		</g>
	);
};

/** A cloth flag on a pole, rippling in the wind. */
const ClothFlag: React.FC<{t: number; x: number; top: number}> = ({t, x, top}) => {
	const w = wind(t);
	const len = 150 + 40 * w;
	const wave = (u: number) => Math.sin(u * 7 - t * (6 + 5 * w)) * (6 + 10 * w) * u;
	const drop = (1 - w) * 60; // a slack flag hangs lower
	const pts = Array.from({length: 9}, (_, i) => i / 8);
	const topEdge = pts.map((u) => `${(x + u * len).toFixed(1)},${(top + u * drop + wave(u)).toFixed(1)}`);
	const bottomEdge = pts.reverse().map((u) => `${(x + u * len * 0.96).toFixed(1)},${(top + 84 + u * drop * 1.2 + wave(u)).toFixed(1)}`);
	return (
		<g>
			<rect x={x - 6} y={top - 16} width={12} height={880 - top + 16} fill="#6b4a2e" {...ink(2.5)} />
			<circle cx={x} cy={top - 20} r={10} fill="#d9b25c" {...ink(2)} />
			<path d={`M${topEdge.join(' L')} L${bottomEdge.join(' L')} Z`} fill="#c8323a" {...ink(3)} />
		</g>
	);
};

const PrayerFlags: React.FC<{t: number}> = ({t}) => {
	const colors = ['#3f6fb5', '#f4efe2', '#c8323a', '#4f9a5a', '#e9c046'];
	const [x0, y0, x1, y1] = [470, 318, 1320, 250];
	const n = 18;
	const w = wind(t);
	return (
		<g>
			<path d={`M${x0},${y0} Q${(x0 + x1) / 2},${(y0 + y1) / 2 + 90} ${x1},${y1}`} fill="none" stroke="#6b5a48" strokeWidth={2.5} />
			{Array.from({length: n}).map((_, i) => {
				const u = (i + 0.5) / n;
				const x = (1 - u) * (1 - u) * x0 + 2 * u * (1 - u) * ((x0 + x1) / 2) + u * u * x1;
				const y = (1 - u) * (1 - u) * y0 + 2 * u * (1 - u) * ((y0 + y1) / 2 + 90) + u * u * y1;
				const lift = (8 + 16 * w) * Math.sin(t * 5 + i * 0.9);
				return (
					<path key={i} d={`M${x - 14},${y} L${x + 14},${y} L${x + 14 + lift * 0.6},${y + 34} L${x - 14 + lift * 0.6},${y + 34} Z`}
						fill={colors[i % colors.length]} opacity={0.92} {...ink(1.5, 0.6)} />
				);
			})}
		</g>
	);
};

const Pine: React.FC<{x: number; y: number; scale: number; t: number}> = ({x, y, scale, t}) => {
	const sway = (wind(t) - 0.5) * 6;
	return (
		<g transform={`translate(${x} ${y}) scale(${scale}) rotate(${sway} 0 0)`}>
			<rect x={-9} y={-60} width={18} height={60} fill="#5d4330" {...ink(2.5)} />
			{[0, 1, 2, 3].map((i) => (
				<path key={i} d={`M${-90 + i * 16},${-50 - i * 62} L0,${-150 - i * 62} L${90 - i * 16},${-50 - i * 62} Z`} fill={i % 2 ? '#4f7248' : '#456a40'} {...ink(3)} />
			))}
		</g>
	);
};

const Hall: React.FC<{lit: boolean}> = ({lit}) => (
	<g>
		{/* walls */}
		<rect x={-220} y={420} width={700} height={400} fill="#efe4cf" {...ink(3.5)} />
		<rect x={-220} y={420} width={700} height={46} fill="#7a2e2a" {...ink(3)} />
		{[0, 1, 2].map((i) => (
			<g key={i}>
				<rect x={-110 + i * 190} y={520} width={96} height={130} rx={6} fill={lit ? '#ffcf7a' : '#4a3a30'} {...ink(3)} />
				<path d={`M${-110 + i * 190},${585} L${-14 + i * 190},${585} M${-62 + i * 190},${520} L${-62 + i * 190},${650}`} stroke="#7a2e2a" strokeWidth={5} />
				{lit && <circle cx={-62 + i * 190} cy={585} r={110} fill="url(#warmGlow)" opacity={0.6} />}
			</g>
		))}
		{/* door */}
		<path d="M360,820 L360,640 Q410,600 460,640 L460,820 Z" fill="#8a3a2e" {...ink(3)} />
		{/* tiered roof */}
		<path d="M-260,428 L520,428 L440,360 L-180,360 Z" fill="#5a2622" {...ink(3.5)} />
		<path d="M-120,362 L380,362 L310,300 L-60,300 Z" fill="#6b2d27" {...ink(3.5)} />
		<path d="M-20,302 L280,302 L220,254 L40,254 Z" fill="#5a2622" {...ink(3.5)} />
		<path d="M130,254 L130,214" stroke="#c9a13b" strokeWidth={10} strokeLinecap="round" />
		<circle cx={130} cy={206} r={12} fill="#d9b25c" {...ink(2.5)} />
	</g>
);

const Target: React.FC = () => {
	const [x, y] = TARGET;
	return (
		<g>
			<path d={`M${x - 40},${y + 10} L${x - 60},${y + 150} M${x + 40},${y + 10} L${x + 60},${y + 150} M${x},${y + 20} L${x + 30},${y + 150}`} stroke="#6b4a2e" strokeWidth={8} strokeLinecap="round" />
			<ellipse cx={x} cy={y} rx={52} ry={56} fill="#e8d9ae" {...ink(3)} />
			<ellipse cx={x} cy={y} rx={38} ry={41} fill="#c8323a" {...ink(1.5)} />
			<ellipse cx={x} cy={y} rx={24} ry={26} fill="#f4efe2" {...ink(1.5)} />
			<ellipse cx={x} cy={y} rx={11} ry={12} fill="#c8323a" {...ink(1.5)} />
		</g>
	);
};

const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const lit = p.light < 0.6;
	return (
		<g>
			<g filter="url(#farBlur)" opacity={0.9}>
				<Peaks y={470} amp={230} color="#9fb0c4" snow="#f4f6f8" seed={301} />
				<Peaks y={600} amp={120} color="#8a9c8c" seed={303} />
			</g>
			{/* valley haze */}
			<rect x={-240} y={600} width={2400} height={140} fill="#f3eee2" opacity={0.35} />
			<Pine x={1860} y={720} scale={1.5} t={t} />
			<Pine x={640} y={712} scale={0.9} t={t + 1.3} />
			<PrayerFlags t={t} />
			<Hall lit={lit} />
			{/* the courtyard's low parapet above the valley */}
			<g>
				<path d="M470,700 L2160,690 L2160,770 L470,780 Z" fill="#b7a98f" {...ink(3)} />
				{Array.from({length: 16}).map((_, i) => (
					<path key={i} d={`M${520 + i * 104},${698 - i * 0.6} L${520 + i * 104},${778 - i * 0.6}`} stroke="#9a8c72" strokeWidth={3} />
				))}
				<path d="M470,700 L2160,690" stroke="#cfc2a8" strokeWidth={8} />
			</g>
			<Target />
			{/* stone paving */}
			<g filter="url(#watercolor)">
				<path d="M-240,770 L2160,760 L2160,1300 L-240,1300 Z" fill="#cbbd9f" />
			</g>
			{Array.from({length: 7}).map((_, r) => (
				<path key={r} d={`M-240,${800 + r * 70 + r * r * 6} L2160,${795 + r * 70 + r * r * 6}`} stroke="#b3a386" strokeWidth={2.5} />
			))}
			{Array.from({length: 26}).map((_, i) => (
				<path key={`v${i}`} d={`M${-200 + i * 96 + (i % 2) * 40},${800} L${-200 + i * 96 + (i % 2) * 40 + (i - 13) * 18},${1300}`} stroke="#b3a386" strokeWidth={2} opacity={0.6} />
			))}
			<Grass y={776} count={40} height={22} color="#8a9a62" seed={307} x0={480} x1={2140} sway={(wind(t) - 0.5) * 8} />
			<ClothFlag t={t} x={FLAG_X} top={430} />
			{/* long stone bench: a seated character's seat */}
			<g>
				<rect x={BENCH[0]} y={750} width={BENCH[1] - BENCH[0]} height={28} rx={6} fill="#a99a82" {...ink(3)} />
				{[BENCH[0] + 40, (BENCH[0] + BENCH[1]) / 2 - 30, BENCH[1] - 100].map((x) => (
					<rect key={x} x={x} y={778} width={60} height={100} fill="#958670" {...ink(3)} />
				))}
			</g>
			{/* butter lamps glow on the hall steps at night */}
			{lit && [300, 520].map((x) => <circle key={x} cx={x} cy={800} r={40} fill="url(#warmGlow)" opacity={0.7 + 0.2 * Math.sin(t * 9 + x)} />)}
		</g>
	);
};

export const location: Location = {
	id: 'monastery-courtyard',
	groundY: 880,
	backgroundGroundY: 790,
	propSlots: [[1560, 880], [420, 880]],
	Background,
};
