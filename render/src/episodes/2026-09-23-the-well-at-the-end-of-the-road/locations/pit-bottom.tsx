import React from 'react';
import {rand, ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// Inside the pit, looking up: brick-lined walls narrowing to a circle of sky, a near rim that someone
// can peek over (a background character stands behind it: only head and shoulders show), a rock ledge a
// sitting character sits on (at center), and a single beam of light falling in.
const Background: React.FC<DrawContext> = ({t, palette: p}) => (
	<g>
		<rect x={-240} y={-240} width={2400} height={1560} fill="#2a1f17" />
		{/* sky through the mouth of the pit */}
		<ellipse cx={960} cy={170} rx={560} ry={150} fill={p.skyTop} />
		<ellipse cx={960} cy={190} rx={560} ry={130} fill={p.skyMid} opacity={0.7} />
		<ellipse cx={960} cy={170} rx={560} ry={150} fill="none" stroke="#a0522d" strokeWidth={14} />
		{/* brick courses, curving round the shaft */}
		{Array.from({length: 9}).map((_, r) => {
			const y = 380 + r * 90;
			return (
				<g key={r} opacity={0.9 - r * 0.05}>
					<path d={`M-240,${y - 120} Q960,${y + 60} 2160,${y - 120}`} fill="none" stroke="#5a3a26" strokeWidth={5} />
					{Array.from({length: 14}).map((_, i) => (
						<path key={i} d={`M${-150 + i * 170 + (r % 2) * 85},${y - 110 + Math.abs(i - 6.5) * -6 + 40} l0,70`} stroke="#5a3a26" strokeWidth={4} opacity={0.7} />
					))}
				</g>
			);
		})}
		{/* the beam of light */}
		<path d="M760,300 L1160,300 L1320,1100 L600,1100 Z" fill="#fff4d6" opacity={0.08 + 0.03 * Math.sin(t * 0.8)} />
		{/* the rock floor and the ledge */}
		<path d="M-240,900 C300,870 1600,880 2160,900 L2160,1300 L-240,1300 Z" fill="#4a3526" />
		<path d="M700,762 C760,744 1160,744 1220,762 L1240,900 L680,900 Z" fill="#5d4535" {...ink(3)} />
		{Array.from({length: 16}).map((_, i) => (
			<ellipse key={i} cx={rand(i, 551) * 1920} cy={930 + rand(i, 553) * 200} rx={14 + rand(i, 555) * 20} ry={8} fill="#5d4535" {...ink(1.5, 0.6)} />
		))}
	</g>
);

/** The near lip of the shaft, drawn over characters: whoever stands behind it only peeks over. */
const Foreground: React.FC<DrawContext> = () => (
	<g>
		<path d="M380,300 Q960,380 1540,300 L1560,420 Q960,500 360,420 Z" fill="#3a2a1e" />
		<path d="M380,300 Q960,380 1540,300" fill="none" stroke="#a0522d" strokeWidth={14} />
		{Array.from({length: 9}).map((_, i) => (
			<path key={i} d={`M${440 + i * 125},${326 + Math.abs(i - 4) * -6 + 30} l0,60`} stroke="#5a3a26" strokeWidth={4} />
		))}
	</g>
);

export const location: Location = {
	id: 'pit-bottom', interior: true, groundY: 900, backgroundGroundY: 420, Foreground,
	propSlots: [[1380, 905], [520, 905]],
	Background,
};
