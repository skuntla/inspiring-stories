import React from 'react';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A cozy round cottage with a small stone fireplace, a worn wooden table and a circular window.
const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const flicker = 0.75 + 0.15 * Math.sin(t * 9) + 0.1 * Math.sin(t * 13.3);
	return (
		<g>
			<g filter="url(#watercolor)">
				{/* curved plaster walls and beams */}
				<rect x={-200} y={-200} width={2320} height={1100} fill="#e8d5b0" />
				<path d="M-200,-60 C400,120 1520,120 2120,-60" fill="none" stroke="#8a6a48" strokeWidth={40} />
				<path d="M-200,160 C500,280 1420,280 2120,160" fill="none" stroke="#e0caa0" strokeWidth={6} opacity={0.6} />
				{/* floorboards */}
				<rect x={-200} y={780} width={2320} height={520} fill="#a97f55" {...ink(3, 0.6)} />
				{Array.from({length: 14}).map((_, i) => (
					<path key={i} d={`M${-200 + i * 170},780 L${-420 + i * 200},1300`} stroke="#8e6842" strokeWidth={3} />
				))}
			</g>
			{/* circular window, showing the time of day */}
			<g>
				<circle cx={1480} cy={380} r={130} fill="#6e5236" {...ink(3.5)} />
				<circle cx={1480} cy={380} r={108} fill={p.skyMid} />
				<circle cx={1480} cy={380} r={108} fill={p.skyTop} opacity={0.5} />
				<path d="M1480,272 L1480,488 M1372,380 L1588,380" stroke="#6e5236" strokeWidth={10} />
			</g>
			{/* stone fireplace with fire */}
			<g>
				<path d="M120,780 L120,420 C120,380 520,380 520,420 L520,780 Z" fill="#9b958b" {...ink(3.5)} />
				{Array.from({length: 16}).map((_, i) => (
					<ellipse key={i} cx={150 + (i % 4) * 100 + (Math.floor(i / 4) % 2) * 40} cy={450 + Math.floor(i / 4) * 80} rx={42} ry={26}
						fill={rand(i, 3) > 0.5 ? '#a8a298' : '#8f897f'} {...ink(2, 0.6)} />
				))}
				<path d="M200,780 L200,600 C200,540 440,540 440,600 L440,780 Z" fill="#2e241c" {...ink(3.5)} />
				<ellipse cx={320} cy={700} rx={170 * flicker} ry={140 * flicker} fill="url(#warmGlow)" />
				<path d={`M250,770 C260,${700 - 30 * flicker} 300,${690 - 40 * flicker} 320,${640 - 50 * flicker} C340,${690 - 40 * flicker} 380,${700 - 30 * flicker} 390,770 Z`}
					fill="#f39a3c" />
				<path d={`M285,770 C295,${720 - 20 * flicker} 315,${710 - 30 * flicker} 322,${690 - 30 * flicker} C330,${715 - 20 * flicker} 350,${725 - 20 * flicker} 355,770 Z`}
					fill="#ffd36a" />
				<rect x={230} y={762} width={180} height={18} rx={8} fill="#5a3a22" {...ink(2.5)} />
				<rect x={90} y={400} width={460} height={34} rx={6} fill="#7a5a3a" {...ink(3)} />
			</g>
			{/* worn wooden table */}
			<g>
				<rect x={1160} y={690} width={520} height={34} rx={8} fill="#9a6e44" {...ink(3.5)} />
				<rect x={1190} y={724} width={26} height={150} fill="#835a36" {...ink(3)} />
				<rect x={1624} y={724} width={26} height={150} fill="#835a36" {...ink(3)} />
				<path d="M1190,705 L1400,707 M1450,712 L1640,709" stroke="#7d5634" strokeWidth={2} opacity={0.7} />
			</g>
		</g>
	);
};

export const location: Location = {
	id: 'pip-cottage-interior',
	interior: true,
	groundY: 880,
	backgroundGroundY: 790,
	propSlots: [[1300, 692], [1440, 692], [1560, 692]],
	Background,
};
