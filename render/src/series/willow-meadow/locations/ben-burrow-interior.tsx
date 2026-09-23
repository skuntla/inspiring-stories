import React from 'react';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A warm round burrow with a stone fireplace, a low wooden table, curved bookshelves and a circular window.
const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const flicker = 0.8 + 0.12 * Math.sin(t * 8.7) + 0.08 * Math.sin(t * 12.1);
	return (
		<g>
			<g filter="url(#watercolor)">
				<rect x={-200} y={-200} width={2320} height={1100} fill="#c9a279" />
				<path d="M-200,-100 C300,260 1620,260 2120,-100 L2120,-200 L-200,-200 Z" fill="#a8835c" {...ink(3, 0.6)} />
				<rect x={-200} y={800} width={2320} height={500} fill="#8a6440" {...ink(3, 0.6)} />
				<ellipse cx={960} cy={900} rx={560} ry={70} fill="#9c3f35" opacity={0.75} {...ink(2.5, 0.6)} />
			</g>
			{/* curved bookshelves */}
			<g>
				<path d="M60,800 L60,300 C160,240 360,240 460,300 L460,800 Z" fill="#6e4a2c" {...ink(3.5)} />
				{[380, 480, 580, 680].map((y, r) => (
					<g key={r}>
						<rect x={80} y={y} width={360} height={10} fill="#5a3a22" />
						{Array.from({length: 11}).map((_, i) => (
							<rect key={i} x={88 + i * 31} y={y - 70 + rand(i, r) * 16} width={24} height={70 - rand(i, r) * 16}
								fill={['#8b3a3a', '#3f6a8a', '#6b8a3f', '#b08a3a'][(i + r) % 4]} {...ink(1.5, 0.7)} />
						))}
					</g>
				))}
			</g>
			{/* circular window */}
			<circle cx={720} cy={300} r={110} fill="#6e5236" {...ink(3.5)} />
			<circle cx={720} cy={300} r={90} fill={p.skyMid} />
			<circle cx={720} cy={300} r={90} fill={p.skyTop} opacity={0.5} />
			<path d="M720,210 L720,390 M630,300 L810,300" stroke="#6e5236" strokeWidth={9} />
			{/* stone fireplace */}
			<g>
				<path d="M1480,800 L1480,440 C1480,400 1840,400 1840,440 L1840,800 Z" fill="#9b958b" {...ink(3.5)} />
				<path d="M1550,800 L1550,620 C1550,560 1770,560 1770,620 L1770,800 Z" fill="#2e241c" {...ink(3.5)} />
				<ellipse cx={1660} cy={720} rx={170 * flicker} ry={130 * flicker} fill="url(#warmGlow)" />
				<path d={`M1600,792 C1610,${720 - 30 * flicker} 1645,${705 - 40 * flicker} 1660,${660 - 45 * flicker} C1675,${705 - 40 * flicker} 1710,${720 - 30 * flicker} 1720,792 Z`} fill="#f39a3c" />
				<path d={`M1630,792 C1640,${740 - 20 * flicker} 1655,${730 - 25 * flicker} 1662,${708 - 25 * flicker} C1670,${732 - 20 * flicker} 1686,${742 - 20 * flicker} 1692,792 Z`} fill="#ffd36a" />
			</g>
			{/* low wooden table */}
			<rect x={780} y={760} width={360} height={26} rx={8} fill="#9a6e44" {...ink(3.5)} />
			<rect x={805} y={786} width={22} height={70} fill="#835a36" {...ink(3)} />
			<rect x={1093} y={786} width={22} height={70} fill="#835a36" {...ink(3)} />
		</g>
	);
};

export const location: Location = {
	id: 'ben-burrow-interior',
	interior: true,
	groundY: 884,
	backgroundGroundY: 800,
	propSlots: [[880, 762], [990, 762], [1090, 762]],
	Background,
};
