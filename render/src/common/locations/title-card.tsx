import React from 'react';
import {Hills} from '../../kit/scenery';
import type {DrawContext, Location} from '../../kit/types';

// The title card after a hook: the narrator says the title and it appears large over soft hills,
// a thin line drawing out beneath it. The music starts here when an episode opens with a hook.
export const about = "Title card: the episode title, as the narrator says it, large over soft hills (captions are hidden); the music starts here.";

const Background: React.FC<DrawContext> = ({t, words}) => {
	const title = (words ?? []).map((w) => w.text).join(' ').replace(/[.!…]+$/, '');
	const fade = Math.min(1, t / 0.9);
	const rise = (1 - fade) * 24;
	const rule = Math.min(1, Math.max(0, (t - 0.4) / 1.2));
	const size = title.length > 26 ? 92 : 112;
	return (
		<g>
			<g filter="url(#farBlur)">
				<Hills y={800} amp={70} color="#b9ab92" seed={401} outline={0.1} />
				<Hills y={900} amp={40} color="#9f957f" seed={403} outline={0.15} />
			</g>
			<g opacity={fade} transform={`translate(0 ${rise})`} fontFamily="Georgia, 'Times New Roman', serif" textAnchor="middle" fill="#3b2a20">
				<text x={960} y={470} fontSize={size} letterSpacing={2}>{title}</text>
				<path d={`M${960 - 260 * rule},540 L${960 + 260 * rule},540`} stroke="#8a5c38" strokeWidth={4} strokeLinecap="round" />
			</g>
		</g>
	);
};

export const location: Location = {id: 'title-card', groundY: 880, propSlots: [], showsText: true, Background};
