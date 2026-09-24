import React from 'react';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';
import {Camel} from '../../../vendor/fluent-emoji/Camel';
import {Counter, Horizon, LeaningShovel, MudHouse, Neem, StoneWell, Villagers} from '../parts/village';

// Years later: the end of the road has become a market. Striped stall awnings and bunting, the well at
// its heart, Velu's counter, and a caravan of camels coming down the road from the horizon.
const Stall: React.FC<{x: number; y: number; color: string; s?: number}> = ({x, y, color, s = 1}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`}>
		<rect x={-110} y={-120} width={220} height={120} fill="#c9a579" {...ink(3)} />
		<path d="M-130,-120 L130,-120 L110,-190 L-110,-190 Z" fill={color} {...ink(3)} />
		{[0, 1, 2, 3, 4].map((i) => <path key={i} d={`M${-110 + i * 55},-190 L${-130 + i * 65},-120`} stroke="#f4efe2" strokeWidth={10} opacity={0.8} />)}
		{[0, 1, 2].map((i) => <circle key={i} cx={-60 + i * 60} cy={-40} r={22} fill={['#e9c046', '#c8323a', '#4f9a5a'][i]} {...ink(2)} />)}
	</g>
);

const Background: React.FC<DrawContext> = ({t, palette: p}) => (
	<g>
		<Horizon t={t} y={620} />
		<path d="M-240,700 L2160,690 L2160,1300 L-240,1300 Z" fill="#dcc095" />
		{/* the road, busy now */}
		<path d="M700,1300 C820,1040 900,860 940,690 L1000,690 C1060,860 1200,1040 1360,1300 Z" fill="#e6cfa4" />
		{/* caravan coming down the road */}
		{[0, 1, 2, 3, 4].map((i) => {
			const u = ((t * 0.035 + i * 0.16) % 1);
			const y = 690 + u * u * 240;
			const s = 60 + u * u * 150;
			return <g key={i} transform={`translate(${960 + (1 - u) * 30 - u * 180} ${y})`} opacity={Math.min(1, u * 6)}><Camel size={s} /></g>;
		})}
		<MudHouse x={140} y={760} scale={0.8} lit={p.light < 0.5} />
		<Stall x={420} y={790} color="#c8323a" s={0.9} />
		<Stall x={660} y={770} color="#3f6fb5" s={0.7} />
		<Stall x={1330} y={770} color="#e9c046" s={0.7} />
		<Stall x={1600} y={790} color="#4f9a5a" s={0.9} />
		{/* bunting */}
		<path d="M200,420 Q960,560 1760,420" fill="none" stroke="#6b5a48" strokeWidth={2.5} />
		{Array.from({length: 22}).map((_, i) => {
			const u = (i + 0.5) / 22;
			const x = 200 + u * 1560;
			const y = 420 + Math.sin(u * Math.PI) * 70;
			return <path key={i} d={`M${x - 16},${y} L${x + 16},${y} L${x + Math.sin(t * 4 + i) * 3},${y + 34} Z`}
				fill={['#c8323a', '#e9c046', '#3f6fb5', '#4f9a5a', '#f4efe2'][i % 5]} {...ink(1.5, 0.6)} />;
		})}
		<Neem x={1840} y={860} scale={1.1} t={t} />
		<Villagers t={t} palette={p} people={[
			{x0: 300, speed: 40, y: 760, scale: 0.28, who: 0},
			{x0: 1100, speed: 36, y: 764, scale: 0.28, who: 1, facing: -1},
			{x0: 1700, speed: 44, y: 762, scale: 0.26, who: 2},
		]} />
		<StoneWell x={1500} y={930} t={t} scale={0.9} />
		<LeaningShovel x={330} y={930} />
		<Counter x={960} y={930} />
		{Array.from({length: 10}).map((_, i) => (
			<ellipse key={i} cx={rand(i, 571) * 1920} cy={1000 + rand(i, 573) * 200} rx={30} ry={6} fill="#c9a579" opacity={0.5} />
		))}
	</g>
);

export const location: Location = {
	id: 'market-road', groundY: 930, backgroundGroundY: 810,
	propSlots: [[920, 790], [1180, 930]],
	Background,
};
