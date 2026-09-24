import React from 'react';
import type {DrawContext, Location} from '../../../kit/types';
import {Counter, CrackedEarth, Horizon, LeaningShovel, MudHouse, Neem, StoneWell, Villagers} from '../parts/village';

// The finished well on Velu's plot: the stone well with its pulley and bucket, the neem tree, Velu's
// wooden counter (between a character at center_left and one at center_right), his hut wall with the
// old shovel leaning on it, and women queueing with their pots.
const Background: React.FC<DrawContext> = ({t, palette: p}) => (
	<g>
		<Horizon t={t} />
		<MudHouse x={200} y={800} scale={1.05} lit={p.light < 0.5} />
		<CrackedEarth y={770} seed={561} tint="#dcc095" />
		{/* a ring of green where the water spills */}
		<ellipse cx={1520} cy={880} rx={380} ry={60} fill="#9bb86a" opacity={0.55} />
		<Neem x={1760} y={860} scale={1.2} t={t} />
		<Villagers t={t} palette={p} people={[
			{x0: 1880, speed: 0, y: 796, scale: 0.42, who: 0, walk: false, facing: -1},
			{x0: 1980, speed: 0, y: 796, scale: 0.42, who: 1, walk: false, facing: -1},
			{x0: 2080, speed: 0, y: 796, scale: 0.42, who: 2, walk: false, facing: -1},
		]} />
		<StoneWell x={1500} y={900} t={t} />
		<LeaningShovel x={330} y={900} />
		<Counter x={960} y={900} />
	</g>
);

export const location: Location = {
	id: 'the-well', groundY: 900, backgroundGroundY: 800,
	propSlots: [[920, 760], [1160, 900]],
	Background,
};
