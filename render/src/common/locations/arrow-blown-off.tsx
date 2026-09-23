import React from 'react';
import {wordAt, wordsAt} from '../../kit/spoken';
import type {DrawContext, Location} from '../../kit/types';
import {Backdrop, BlownArrow, WindStreaks} from '../parts/archery';

// Close on the target: an arrow flies in straight for the center, a gust sweeps across, and the arrow
// turns away above the target. Timed to the voice: the gust lands on "wind" / "push" / "turn", and
// every "again" / "another" sends one more arrow the same way.
export const about = "Close-up of an archery target: an arrow flies for the center and a gust blows it away; each spoken 'again' fires another.";

const GUST_AFTER = 0.55;

const Background: React.FC<DrawContext> = ({t, words}) => {
	const gustWord = wordAt(words, /^(wind|push|turn|blew|blow)/i);
	const first = gustWord !== undefined ? Math.max(0.1, gustWord - GUST_AFTER) : 0.3;
	const more = wordsAt(words, /^(again|another)/i).filter((w) => w > first + 0.6);
	const launches = [first, ...more];
	return (
		<g>
			<Backdrop t={t} />
			{launches.map((l, i) => <BlownArrow key={i} t={t} launch={l} gustAfter={GUST_AFTER} seed={i} />)}
			<WindStreaks t={t} at={launches.map((l) => l + GUST_AFTER)} gentle />
		</g>
	);
};

export const location: Location = {id: 'arrow-blown-off', groundY: 1040, propSlots: [], Background};
