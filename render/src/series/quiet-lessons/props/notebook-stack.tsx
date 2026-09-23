import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A leaning stack of half-used notebooks in faded blue, red and green covers.
const COVERS = ['#5d7f91', '#b8653a', '#6d8b4a', '#8a6a9a', '#c9a24a'];

const Stack: React.FC<DrawContext> = () => (
	<g filter="url(#softEdge)">
		{COVERS.map((c, i) => (
			<g key={i} transform={`translate(${(i % 2 ? 6 : -4) + i * 1.5} ${-i * 22}) rotate(${(i % 2 ? 3 : -2)})`}>
				<rect x={-60} y={-22} width={120} height={22} rx={3} fill={c} {...ink(2.5)} />
				<rect x={-54} y={-16} width={108} height={4} fill="#f3eee2" opacity={0.7} />
			</g>
		))}
	</g>
);

export const prop: Prop = {id: 'notebook-stack', width: 130, Component: Stack};
