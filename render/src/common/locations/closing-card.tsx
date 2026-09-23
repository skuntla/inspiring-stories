import React from 'react';
import {Hills} from '../../kit/scenery';
import {sentences, wrap} from '../../kit/spoken';
import type {DrawContext, Location} from '../../kit/types';

// A closing card: the shot's spoken words as a quote over soft hills under the time-of-day sky.
export const about = "Closing card: the shot's narration shown as a quote over soft hills (captions are hidden).";

const CHARS = 38; // per quote line at this size

const Background: React.FC<DrawContext> = ({t, words}) => {
	const fade = Math.min(1, t / 1.4);
	const lines = React.useMemo(() => sentences(words).flatMap((s) => wrap(s.text, CHARS)), [words]); // each sentence starts a line
	const size = lines.length > 3 ? 54 : 62;
	const top = 300 - ((lines.length - 1) * size * 1.35) / 2;
	return (
		<g>
			<g filter="url(#farBlur)">
				<Hills y={760} amp={60} color="#c9b8a0" seed={81} outline={0.1} />
				<Hills y={860} amp={40} color="#a9a08a" seed={83} outline={0.15} />
			</g>
			<g opacity={fade} fontFamily="Georgia, 'Times New Roman', serif" fontStyle="italic" textAnchor="middle" fill="#3b2a20">
				{lines.map((line, i) => (
					<text key={i} x={960} y={top + i * size * 1.35} fontSize={size}>
						{line}
					</text>
				))}
			</g>
		</g>
	);
};

export const location: Location = {
	id: 'closing-card',
	groundY: 880,
	propSlots: [],
	showsText: true,
	Background,
};
