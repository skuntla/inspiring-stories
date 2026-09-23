import React from 'react';
import {Flowers, Grass, Hills, Tree} from '../../../kit/scenery';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A quiet neighbourhood park with a wooden bench, tall trees, a lamp post and a bed of young plants.
const BENCH_X = 672; // a seated character at position center_left sits on it

const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const sway = Math.sin(t * 1.1) * 3;
	const lampOn = p.light < 0.65;
	return (
		<g>
			<g filter="url(#farBlur)" opacity={0.85}>
				<Hills y={600} amp={50} color="#a9b7a0" seed={61} outline={0.12} />
				<Tree x={1500} y={620} scale={0.8} leaf="#8f9f84" trunk="#7d8a74" outline={0} />
			</g>
			<g filter="url(#watercolor)">
				<Hills y={740} amp={20} color="#8ba06a" seed={63} waves={3} outline={0.45} />
				<path d="M-200,860 C300,840 900,850 2120,830 L2120,900 C900,920 300,910 -200,930 Z" fill="#d8c7a0" {...ink(3, 0.5)} />
			</g>
			<g transform={`rotate(${sway} 260 860)`}><Tree x={260} y={860} scale={2.1} leaf="#6f9150" trunk="#6b4f38" /></g>
			<g transform={`rotate(${-sway * 0.8} 1760 850)`}><Tree x={1760} y={850} scale={1.8} leaf="#7c9a58" trunk="#6b4f38" /></g>
			{/* lamp post, lit at dusk and night */}
			<g>
				{lampOn && <circle cx={1090} cy={420} r={150} fill="url(#warmGlow)" />}
				<rect x={1082} y={430} width={16} height={440} fill="#3b3a3a" {...ink(2.5)} />
				<path d="M1062,430 L1118,430 L1106,392 L1074,392 Z" fill={lampOn ? '#ffd98a' : '#e8e2d0'} {...ink(3)} />
			</g>
			{/* bed of young plants */}
			<g>
				<path d="M1280,880 L1300,830 L1880,830 L1900,880 Z" fill="#6b4a32" {...ink(3)} />
				{Array.from({length: 14}).map((_, i) => (
					<path key={i} d={`M${1320 + i * 40},832 q-10,-24 0,-34 q10,10 0,34`} fill="#7cba5a" {...ink(1.5)} />
				))}
			</g>
			<Flowers y0={880} y1={960} count={20} color="#e9a23b" seed={65} />
			<Grass y={900} count={50} height={40} color="#7d9360" seed={67} />
			{/* bench: back rest and seat behind a sitter at BENCH_X */}
			<g>
				<rect x={BENCH_X - 150} y={650} width={300} height={22} rx={6} fill="#8a5c38" {...ink(3)} />
				<rect x={BENCH_X - 150} y={690} width={300} height={22} rx={6} fill="#8a5c38" {...ink(3)} />
				<rect x={BENCH_X - 170} y={750} width={340} height={24} rx={6} fill="#9a6a42" {...ink(3)} />
				<rect x={BENCH_X - 150} y={774} width={16} height={100} fill="#3b3a3a" {...ink(2.5)} />
				<rect x={BENCH_X + 134} y={774} width={16} height={100} fill="#3b3a3a" {...ink(2.5)} />
			</g>
		</g>
	);
};

const Foreground: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)">
		<Grass y={1150} count={30} height={140} color="#6c8450" seed={69} sway={Math.sin(t * 1.3) * 5} />
	</g>
);

export const location: Location = {
	id: 'city-park',
	groundY: 880,
	backgroundGroundY: 800,
	propSlots: [[1420, 884], [1720, 886]],
	Background,
	Foreground,
};
