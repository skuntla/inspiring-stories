import React from 'react';
import type {DrawContext, Prop} from '../../../kit/types';

// Clear spring water pooling at the bottom of the pit, bubbling and rippling.
const Pool: React.FC<DrawContext> = ({t}) => (
	<g>
		<ellipse cx={0} cy={0} rx={320} ry={40} fill="#3f7fa6" />
		<ellipse cx={-40} cy={-6} rx={220} ry={20} fill="#8fc3e0" opacity={0.6} />
		{[0, 1, 2].map((i) => {
			const k = (t * 0.5 + i / 3) % 1;
			return <ellipse key={i} cx={0} cy={0} rx={40 + 260 * k} ry={6 + 30 * k} fill="none" stroke="#e6f4fb" strokeWidth={3} opacity={1 - k} />;
		})}
		{[0, 1, 2, 3].map((i) => {
			const k = (t * 1.3 + i / 4) % 1;
			return <circle key={`b${i}`} cx={-20 + i * 14} cy={-6 - k * 30} r={5 - k * 3} fill="#e6f4fb" opacity={1 - k} />;
		})}
	</g>
);
export const prop: Prop = {id: 'spring-pool', width: 640, Component: Pool};
