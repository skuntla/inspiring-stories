import React from 'react';
import {makeHuman} from '../../../kit/human';
import {Hills} from '../../../kit/scenery';
import {ink, rand} from '../../../kit/style';
import type {Palette} from '../../../kit/types';

// The dry village at the end of the road: shared drawing for this episode's locations.

export const EARTH = '#d9b98a';
export const EARTH_DARK = '#b8946a';

/** The far, flat, sun-bleached horizon with low hills and a shimmer of heat. */
export const Horizon: React.FC<{t: number; y?: number}> = ({t, y = 640}) => (
	<g>
		<g filter="url(#farBlur)" opacity={0.85}>
			<Hills y={y - 40} amp={40} color="#d8c3a0" seed={501} outline={0.1} />
			<Hills y={y} amp={22} color="#cdb08a" seed={503} outline={0.15} />
		</g>
		{[0, 1, 2].map((i) => (
			<path key={i} d={`M${-100 + i * 700 + Math.sin(t * 0.7 + i) * 30},${y - 20 + i * 8} q120,-8 240,0 t240,0`} fill="none" stroke="#fff6e0"
				strokeWidth={3} opacity={0.35 + 0.15 * Math.sin(t * 1.3 + i)} />
		))}
	</g>
);

/** Dry, cracked ground from `y` down, with a web of cracks. */
export const CrackedEarth: React.FC<{y: number; seed?: number; tint?: string}> = ({y, seed = 511, tint = EARTH}) => (
	<g>
		<g filter="url(#watercolor)">
			<rect x={-240} y={y} width={2400} height={1300 - y} fill={tint} />
		</g>
		{Array.from({length: 26}).map((_, i) => {
			const x = -150 + rand(i, seed) * 2200;
			const cy = y + 30 + rand(i, seed + 1) * (1220 - y);
			const s = 0.6 + (cy - y) / 500;
			const pts = [0, 1, 2, 3].map((k) => `${(x + (k * 38 + rand(i * 7 + k, seed + 2) * 30) * s).toFixed(0)},${(cy + (rand(i * 5 + k, seed + 3) - 0.5) * 26 * s).toFixed(0)}`);
			return <path key={i} d={`M${pts.join(' L')}`} fill="none" stroke={EARTH_DARK} strokeWidth={2.2 * s} strokeLinejoin="round" opacity={0.8} />;
		})}
	</g>
);

/** A small mud house with a thatched roof; `broken` leaves a gap in the roof (an abandoned home). */
export const MudHouse: React.FC<{x: number; y: number; scale?: number; broken?: boolean; lit?: boolean}> = ({x, y, scale = 1, broken, lit}) => (
	<g transform={`translate(${x} ${y}) scale(${scale})`}>
		<rect x={-110} y={-150} width={220} height={150} rx={8} fill="#c9a579" {...ink(3)} />
		<path d="M-110,-40 L110,-40" stroke="#b8946a" strokeWidth={3} opacity={0.6} />
		<path d="M-30,0 L-30,-86 Q0,-104 30,-86 L30,0 Z" fill={lit ? '#e8a54a' : '#5a3f2a'} {...ink(3)} />
		<rect x={52} y={-110} width={34} height={30} fill={lit ? '#ffcf7a' : '#5a3f2a'} {...ink(2.5)} />
		<path d={broken ? 'M-140,-146 L-20,-236 L10,-210 L-10,-190 L40,-200 L140,-146 Z' : 'M-140,-146 L0,-246 L140,-146 Z'} fill="#9c7a44" {...ink(3.5)} />
		{Array.from({length: 7}).map((_, i) => (
			<path key={i} d={`M${-120 + i * 36},-150 L${-60 + i * 18},-212`} stroke="#7e5f32" strokeWidth={3} opacity={broken && i > 1 && i < 4 ? 0 : 0.7} />
		))}
	</g>
);

/** The neem tree that stays green: a round, deep-green crown that sways a little. */
export const Neem: React.FC<{x: number; y: number; scale?: number; t: number}> = ({x, y, scale = 1, t}) => {
	const sway = Math.sin(t * 0.9) * 2;
	return (
		<g transform={`translate(${x} ${y}) scale(${scale})`}>
			<path d="M-18,0 C-14,-90 -26,-170 -8,-250 L14,-250 C24,-170 14,-90 20,0 Z" fill="#6b4f38" {...ink(3)} />
			<path d="M0,-200 C-40,-230 -70,-240 -90,-260 M4,-220 C40,-250 70,-262 96,-270" stroke="#6b4f38" strokeWidth={12} strokeLinecap="round" />
			<g transform={`rotate(${sway} 0 -250)`}>
				{[[-110, -300, 95], [0, -350, 120], [110, -300, 95], [-60, -410, 85], [70, -420, 80], [0, -250, 90]].map(([cx, cy, r], i) => (
					<circle key={i} cx={cx} cy={cy} r={r} fill={i % 2 ? '#4f7a3c' : '#5d8a45'} {...ink(3)} />
				))}
				{Array.from({length: 18}).map((_, i) => (
					<path key={i} d={`M${-150 + rand(i, 521) * 300},${-460 + rand(i, 523) * 240} q6,-8 12,0`} fill="none" stroke="#7fa65a" strokeWidth={3} />
				))}
			</g>
		</g>
	);
};

/** A thorny dry bush. */
export const DryBush: React.FC<{x: number; y: number; scale?: number; seed: number}> = ({x, y, scale = 1, seed}) => (
	<g transform={`translate(${x} ${y}) scale(${scale})`} stroke="#8a6a44" strokeWidth={3} strokeLinecap="round" fill="none">
		{Array.from({length: 9}).map((_, i) => {
			const a = -Math.PI * (0.15 + rand(i, seed) * 0.7);
			const l = 40 + rand(i, seed + 1) * 50;
			return <path key={i} d={`M0,0 L${Math.cos(a) * l},${Math.sin(a) * l} m-8,4 l8,-4 l-2,10`} />;
		})}
	</g>
);

/** The stone well: a round stone ring, a wooden frame and pulley, a rope and a bucket that bobs. */
export const StoneWell: React.FC<{x: number; y: number; t: number; scale?: number; water?: boolean; dead?: boolean}> = ({x, y, t, scale = 1, water = true, dead}) => {
	const bob = dead ? 0 : Math.sin(t * 1.6) * 6;
	return (
		<g transform={`translate(${x} ${y}) scale(${scale})`}>
			{/* frame and pulley */}
			<path d="M-120,-150 L-110,-330 M120,-150 L110,-330 M-130,-330 L130,-330" stroke="#6b4a2e" strokeWidth={16} strokeLinecap="round" />
			<path d="M-120,-150 L-110,-330 M120,-150 L110,-330 M-130,-330 L130,-330" stroke="#3b2a20" strokeWidth={3} opacity={0.4} />
			<circle cx={0} cy={-330} r={20} fill="#8a6a44" {...ink(3)} />
			<path d={`M0,-330 L0,${-210 + bob}`} stroke="#c9b27a" strokeWidth={4} opacity={dead ? 0.5 : 1} />
			{!dead && (
				<g transform={`translate(0 ${-210 + bob})`}>
					<path d="M-26,0 L26,0 L20,44 L-20,44 Z" fill="#8a5a2b" {...ink(3)} />
					<path d="M-26,0 Q0,-26 26,0" fill="none" stroke="#3b2a20" strokeWidth={3} />
				</g>
			)}
			{/* the ring of stones */}
			<ellipse cx={0} cy={-150} rx={150} ry={36} fill={water ? '#2f5f7a' : '#3e2f22'} {...ink(3.5)} />
			{water && <ellipse cx={-30} cy={-154} rx={60} ry={8} fill="#8fc3e0" opacity={0.5 + 0.2 * Math.sin(t * 2)} />}
			<path d="M-150,-150 L-150,0 Q0,30 150,0 L150,-150 Q0,-114 -150,-150 Z" fill="#b7a98f" {...ink(3.5)} />
			{Array.from({length: 4}).map((_, r) => (
				<path key={r} d={`M-150,${-120 + r * 34} Q0,${-86 + r * 34} 150,${-120 + r * 34}`} fill="none" stroke="#958670" strokeWidth={3} />
			))}
			{Array.from({length: 12}).map((_, i) => (
				<path key={`v${i}`} d={`M${-138 + i * 24},${-140 + (i % 2) * 34 + Math.abs(i - 6) * 1.5} l0,30`} stroke="#958670" strokeWidth={3} />
			))}
		</g>
	);
};

/** Velu's wooden counter: a notebook, a bowl of copper coins and a brass cup on top. */
export const Counter: React.FC<{x: number; y: number}> = ({x, y}) => (
	<g transform={`translate(${x} ${y})`}>
		<rect x={-160} y={-140} width={320} height={24} rx={6} fill="#9a6a42" {...ink(3)} />
		<rect x={-140} y={-116} width={22} height={116} fill="#7a5234" {...ink(2.5)} />
		<rect x={118} y={-116} width={22} height={116} fill="#7a5234" {...ink(2.5)} />
		<rect x={-130} y={-90} width={260} height={14} fill="#7a5234" {...ink(2)} />
		{/* notebook */}
		<path d="M-120,-140 L-40,-146 L-40,-140 L-120,-134 Z" fill="#8a3a2e" {...ink(2)} />
		<path d="M-116,-146 L-80,-150 L-44,-146 L-80,-142 Z" fill="#f4efe2" {...ink(1.5)} />
		{/* bowl of copper coins */}
		<path d="M10,-140 Q40,-120 70,-140 Z" fill="#6b4a2e" {...ink(2)} />
		{[0, 1, 2, 3].map((i) => <ellipse key={i} cx={24 + i * 10} cy={-143 - (i % 2) * 3} rx={8} ry={3} fill="#d9894a" {...ink(1)} />)}
		{/* brass cup */}
		<path d="M100,-140 L96,-170 L124,-170 L120,-140 Z" fill="#d9a441" {...ink(2)} />
	</g>
);

/** An old iron shovel leaning against something at (x, y). */
export const LeaningShovel: React.FC<{x: number; y: number}> = ({x, y}) => (
	<g transform={`translate(${x} ${y}) rotate(-14)`}>
		<path d="M0,-300 L0,-60" stroke="#3b2a20" strokeWidth={14} strokeLinecap="round" />
		<path d="M0,-300 L0,-60" stroke="#8a6040" strokeWidth={8} strokeLinecap="round" />
		<path d="M-14,-312 L14,-312" stroke="#3b2a20" strokeWidth={9} strokeLinecap="round" />
		<path d="M-24,-64 L24,-64 L20,-4 Q0,10 -20,-4 Z" fill="#7d8288" {...ink(3)} />
		<path d="M-14,-40 L10,-30" stroke="#a0662e" strokeWidth={5} opacity={0.6} />
	</g>
);

/** Village women in the background, each with a clay pot on her head. */
const WOMEN = [
	makeHuman({skin: '#9a6443', skinShade: '#7e4f33', hair: {color: '#1f1814', style: 'bun'}, brows: '#1f1814', shirt: '#3f6fb5', shirtShade: '#325a94',
		sleeves: 'rolled', skirt: {color: '#3f6fb5', shade: '#325a94', hem: -40}, robe: {sash: '#5b86c8'}, pants: '#9a6443', shoes: '#6b4a2e'}),
	makeHuman({skin: '#a86f48', skinShade: '#8c5a3a', hair: {color: '#1f1814', style: 'bun'}, brows: '#1f1814', shirt: '#4f9a5a', shirtShade: '#3f8049',
		sleeves: 'rolled', skirt: {color: '#c8323a', shade: '#9e2530', hem: -40}, robe: {sash: '#c8323a'}, pants: '#a86f48', shoes: '#6b4a2e'}),
	makeHuman({skin: '#8d5a3b', skinShade: '#744831', hair: {color: '#2a1d16', style: 'bun'}, brows: '#2a1d16', shirt: '#e0a33a', shirtShade: '#c4862a',
		sleeves: 'rolled', skirt: {color: '#7a2e2a', shade: '#5e211e', hem: -40}, robe: {sash: '#7a2e2a'}, pants: '#8d5a3b', shoes: '#6b4a2e'}),
];

const HeadPot: React.FC = () => (
	<g transform="translate(8 -486)">
		<path d="M-44,-4 C-50,-60 -20,-80 0,-80 C20,-80 50,-60 44,-4 Z" fill="#b5602f" {...ink(3)} />
		<path d="M-16,-80 L-18,-96 L18,-96 L16,-80" fill="#a3542a" {...ink(2.5)} />
		<path d="M-40,-36 Q0,-26 40,-36" fill="none" stroke="#f4efe2" strokeWidth={4} />
	</g>
);

type Walker = {x0: number; speed: number; y: number; scale: number; who: number; facing?: 1 | -1; walk?: boolean; pot?: boolean};

/** Background villagers: walking (sliding along with their stride) or standing, each drawn small. */
export const Villagers: React.FC<{t: number; palette: Palette; people: Walker[]}> = ({t, palette, people}) => (
	<g>
		{people.map((w, i) => {
			const Woman = WOMEN[w.who % WOMEN.length];
			const walking = w.walk !== false;
			const span = 2400;
			const x = walking ? ((((w.x0 + w.speed * t * (w.facing ?? 1) + 240) % span) + span) % span) - 240 : w.x0;
			return (
				<g key={i} transform={`translate(${x} ${w.y}) scale(${(w.facing ?? 1) * w.scale} ${w.scale})`}>
					<Woman t={t + i} palette={palette} timeOfDay="morning" stance={walking ? 'walk' : 'stand'} mood="neutral" mouth="rest" eye={1}
						speaking={false} facing={(w.facing ?? 1) === 1 ? 'right' : 'left'} walkSpeed={walking ? w.speed / w.scale : 0} />
					{w.pot !== false && <HeadPot />}
				</g>
			);
		})}
	</g>
);
