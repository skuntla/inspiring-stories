import React from 'react';
import {Grass, Hills, Mint, Stone} from '../../../kit/scenery';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// A narrow clear stream bordered by rounded grey stones, bright wild mint and damp grass.
const Background: React.FC<DrawContext> = ({t}) => (
	<g>
		<g filter="url(#farBlur)"><Hills y={620} amp={50} color="#a9b7a8" seed={41} outline={0.15} /></g>
		<g filter="url(#watercolor)">
			<Hills y={700} amp={25} color="#8ba06a" seed={43} waves={3} outline={0.45} />
			{/* the stream runs across the middle ground; the near bank is where characters stand */}
			<path d="M-200,735 C300,710 700,760 1100,742 C1500,725 1800,760 2120,748 L2120,815 C1800,828 1500,792 1100,810 C700,828 300,780 -200,805 Z"
				fill="#8fb3c4" {...ink(3, 0.6)} />
		</g>
		{/* ripples drift downstream */}
		{Array.from({length: 18}).map((_, i) => {
			const x = ((rand(i, 45) * 2320 + t * 60) % 2320) - 200;
			const y = 752 + rand(i, 46) * 45;
			return <path key={i} d={`M${x},${y} q30,-8 60,0`} fill="none" stroke="#e6f2f6" strokeWidth={3} strokeLinecap="round" opacity={0.7} />;
		})}
		{[[180, 812, 110, 44], [460, 822, 130, 50], [880, 808, 100, 40], [1500, 824, 120, 48], [1780, 814, 110, 44]].map(([x, y, w, h], i) => (
			<Stone key={i} x={x} y={y} w={w} h={h} />
		))}
		{/* the rounded streamside stone Wren perches on */}
		<Stone x={1248} y={874} w={130} h={58} moss />
		<Mint x={1000} y={875} seed={47} />
		<Mint x={1600} y={880} scale={0.9} seed={48} />
		<Grass y={880} count={40} height={45} color="#7d9360" seed={49} x0={-200} x1={2120} />
	</g>
);

export const location: Location = {
	id: 'willow-stream',
	groundY: 874,
	backgroundGroundY: 800,
	propSlots: [[520, 884], [610, 890]],
	Background,
};
