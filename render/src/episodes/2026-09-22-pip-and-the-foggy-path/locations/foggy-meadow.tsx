import React from 'react';
import {Grass, Hills} from '../../../kit/scenery';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// An open meadow covered in dense silver fog, with wet grass, faint tree shapes and familiar
// landmarks reduced to shadowy silhouettes (including the crooked thornbush Pip mistakes for the oak).
const Background: React.FC<DrawContext> = ({t}) => (
	<g>
		<rect x={-200} y={-200} width={2320} height={1480} fill="#cfd3cf" />
		<g filter="url(#farBlur)" opacity={0.35}>
			{[180, 620, 1650].map((x, i) => (
				<g key={i} transform={`translate(${x} ${560 + i * 10}) scale(${0.8 + i * 0.15})`}>
					<path d="M-12,0 C-10,-60 -14,-110 -6,-150 L8,-150 C14,-110 10,-60 14,0 Z" fill="#7e847f" />
					<ellipse cx={0} cy={-200} rx={110} ry={75} fill="#8a908b" />
				</g>
			))}
		</g>
		<g filter="url(#watercolor)">
			<Hills y={720} amp={30} color="#a7b09f" seed={31} outline={0.25} />
			<Hills y={800} amp={18} color="#96a18b" seed={33} waves={3} outline={0.4} />
		</g>
		{/* the crooked thornbush, a dark shape in the fog */}
		<g transform="translate(1560 790)" opacity={0.85}>
			{Array.from({length: 9}).map((_, i) => {
				const a = -150 + i * 16 + rand(i, 5) * 10;
				const r = 140 + rand(i, 6) * 60;
				const x = Math.cos((a * Math.PI) / 180) * r;
				const y = Math.sin((a * Math.PI) / 180) * r;
				return <path key={i} d={`M0,0 Q${x * 0.4},${y * 0.7 - 20} ${x},${y}`} fill="none" stroke="#3f423c" strokeWidth={9 - i * 0.5} strokeLinecap="round" />;
			})}
			<ellipse cx={0} cy={-60} rx={150} ry={80} fill="#4a4e47" opacity={0.55} />
		</g>
		<Grass y={840} count={80} height={55} color="#8a9a7e" seed={35} sway={Math.sin(t * 1.2) * 4} />
		{/* wet grass glints */}
		{Array.from({length: 30}).map((_, i) => (
			<circle key={i} cx={-100 + rand(i, 37) * 2120} cy={820 + rand(i, 38) * 200} r={2.5} fill="#ffffff"
				opacity={0.35 + 0.35 * Math.abs(Math.sin(t * 1.5 + i))} />
		))}
	</g>
);

const Foreground: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)">
		<Grass y={1150} count={40} height={170} color="#7d8b71" seed={39} sway={Math.sin(t * 1.3) * 5} />
	</g>
);

export const location: Location = {
	id: 'foggy-meadow',
	groundY: 872,
	backgroundGroundY: 790,
	// basket, buns, then the mossy stone Wren perches on (she stands center-right)
	propSlots: [[520, 882], [620, 888], [1248, 874]],
	Background,
	Foreground,
};
