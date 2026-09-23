import React from 'react';
import {Fence, Flowers, Grass, Hills, Tree, Willow} from '../../../kit/scenery';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A narrow pale-earth path winding through tall muted-green grass, with rolling hills,
// scattered purple flowers and an old wooden fence.
const Background: React.FC<DrawContext> = ({t}) => {
	const sway = Math.sin(t * 1.4) * 6;
	return (
		<g>
			<g filter="url(#farBlur)" opacity={0.9}>
				<Hills y={560} amp={70} color="#a9b7a8" seed={1} outline={0.15} />
				<g opacity={0.55}><Tree x={1500} y={560} scale={0.7} leaf="#8e9d8a" trunk="#7d8a78" outline={0} /></g>
			</g>
			<g filter="url(#watercolor)">
				<Hills y={660} amp={60} color="#94a77d" seed={3} />
				<Willow x={330} y={690} scale={1} t={t} />
				<Fence x0={1080} y0={740} x1={1860} y1={780} posts={7} seed={40} />
				<Hills y={760} amp={25} color="#8ba06a" seed={5} waves={3} outline={0.45} />
				<path d="M1180,745 C1020,790 880,820 790,890 C710,960 650,1040 610,1300 L1090,1300 C1070,1080 1090,970 1160,890 C1220,830 1270,790 1310,750 Z"
					fill="#d8c7a0" {...ink(3, 0.55)} />
				<Flowers y0={770} y1={900} count={28} color="#9b7bb8" seed={7} />
			</g>
			<Grass y={800} count={70} height={60} color="#7d9360" seed={11} sway={sway * 0.5} />
		</g>
	);
};

const Foreground: React.FC<DrawContext> = ({t}) => {
	const sway = Math.sin(t * 1.4) * 6;
	return (
		<g filter="url(#softEdge)">
			<Grass y={1140} count={46} height={190} color="#6c8450" seed={70} sway={sway} />
			<Grass y={1150} count={30} height={120} color="#5e7646" seed={140} sway={sway * 1.3} />
		</g>
	);
};

export const location: Location = {
	id: 'willow-meadow-path',
	groundY: 870,
	backgroundGroundY: 760,
	propSlots: [[1200, 880], [1340, 876], [540, 886]],
	Background,
	Foreground,
};
