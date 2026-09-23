import React from 'react';
import {Grass, Tree} from '../../../kit/scenery';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A narrow residential lane with low painted houses, a neem tree, a garden wall and wires overhead.
const HOUSES = [
	{x: -220, w: 420, h: 330, wall: '#e9c46a', door: '#3f7f86'},
	{x: 200, w: 360, h: 390, wall: '#e9a0a0', door: '#8a5a2e'},
	{x: 560, w: 440, h: 300, wall: '#9fc5c1', door: '#b8653a'},
	{x: 1000, w: 380, h: 360, wall: '#f1e6d2', door: '#6d8b4a'},
	{x: 1380, w: 420, h: 320, wall: '#d9b25c', door: '#3f7f86'},
	{x: 1800, w: 420, h: 380, wall: '#c9b8e0', door: '#8a5a2e'},
];

const Background: React.FC<DrawContext> = ({t}) => (
	<g>
		<g filter="url(#watercolor)">
			{HOUSES.map((h, i) => {
				const top = 780 - h.h;
				return (
					<g key={i}>
						<rect x={h.x} y={top} width={h.w} height={h.h} fill={h.wall} {...ink(3, 0.8)} />
						<rect x={h.x - 10} y={top - 18} width={h.w + 20} height={22} fill="#b8a888" {...ink(2.5, 0.8)} />
						<rect x={h.x + h.w * 0.4} y={780 - 150} width={70} height={150} rx={6} fill={h.door} {...ink(2.5)} />
						{[0.15, 0.7].map((f, j) => (
							<g key={j}>
								<rect x={h.x + h.w * f} y={top + 70} width={70} height={80} fill="#5d7f91" {...ink(2.5)} />
								<path d={`M${h.x + h.w * f + 35},${top + 70} L${h.x + h.w * f + 35},${top + 150}`} stroke="#3b2a20" strokeWidth={3} />
								{rand(i, j) > 0.5 && <rect x={h.x + h.w * f - 8} y={top + 150} width={86} height={12} fill="#8a5a2e" {...ink(2)} />}
							</g>
						))}
					</g>
				);
			})}
			<rect x={-200} y={780} width={2320} height={520} fill="#cdb894" {...ink(3, 0.5)} />
			<path d="M-200,860 L2120,840" stroke="#bda57e" strokeWidth={6} />
		</g>
		{/* wires overhead, swaying a little */}
		<path d={`M-200,180 Q860,${260 + Math.sin(t) * 6} 2120,170`} fill="none" stroke="#3b3a3a" strokeWidth={3} />
		<path d={`M-200,220 Q860,${300 + Math.sin(t + 1) * 6} 2120,210`} fill="none" stroke="#3b3a3a" strokeWidth={3} />
		<rect x={1640} y={120} width={20} height={680} fill="#7a7a74" {...ink(2.5)} />
		<Tree x={420} y={800} scale={1.6} leaf="#6f9150" trunk="#6b4f38" />
		<Grass y={800} count={20} height={30} color="#8a9a5c" seed={71} x0={-200} x1={400} />
	</g>
);

export const location: Location = {
	id: 'morning-lane',
	groundY: 872,
	backgroundGroundY: 810,
	propSlots: [[1450, 876], [1560, 880]],
	Background,
};
