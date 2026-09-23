import React from 'react';
import {Fence, Grass, Hills, Mint, Tree} from '../../../kit/scenery';
import type {DrawContext, Location} from '../../../kit/types';

// A crooked weathered wooden fence beside wild mint, a moss-covered stone and the distant
// silhouette of a great oak tree.
const Background: React.FC<DrawContext> = ({t}) => (
	<g>
		<g filter="url(#farBlur)" opacity={0.6}>
			<Hills y={600} amp={60} color="#a9b7a8" seed={51} outline={0.1} />
			<Tree x={1560} y={600} scale={1.1} leaf="#8e9d8a" trunk="#7d8a78" outline={0} />
		</g>
		<g filter="url(#watercolor)">
			<Hills y={780} amp={24} color="#8ba06a" seed={53} waves={3} outline={0.45} />
			<Fence x0={520} y0={800} x1={1500} y1={790} posts={8} seed={55} color="#7f6a52" />
		</g>
		<Grass y={860} count={60} height={50} color="#7d9360" seed={57} sway={Math.sin(t * 1.3) * 4} />
	</g>
);

const Foreground: React.FC<DrawContext> = () => (
	<g>
		<Mint x={140} y={1080} scale={1.6} seed={58} />
		<Mint x={330} y={1100} scale={1.3} seed={59} />
		<Mint x={1800} y={1090} scale={1.5} seed={60} />
	</g>
);

export const location: Location = {
	id: 'old-fence-crossing',
	groundY: 874,
	backgroundGroundY: 800,
	propSlots: [[1450, 882], [1560, 888], [1120, 878]],
	Background,
	Foreground,
};
