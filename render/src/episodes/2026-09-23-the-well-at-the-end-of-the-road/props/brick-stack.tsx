import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A stack of hand-baked red-brown bricks.
const Bricks: React.FC<DrawContext> = () => (
	<g>
		{Array.from({length: 5}).map((_, r) =>
			Array.from({length: 4 - (r > 2 ? 1 : 0)}).map((_, i) => (
				<rect key={`${r}-${i}`} x={-100 + i * 50 + (r % 2) * 25} y={-26 - r * 24} width={48} height={22} rx={3} fill={i % 2 ? '#a0522d' : '#b0603a'} {...ink(2)} />
			)),
		)}
	</g>
);
export const prop: Prop = {id: 'brick-stack', width: 220, Component: Bricks};
