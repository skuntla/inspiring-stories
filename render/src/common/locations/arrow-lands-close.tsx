import React from 'react';
import {lastWordAt, wordAt} from '../../kit/spoken';
import type {DrawContext, Location} from '../../kit/types';
import {Backdrop, CurvingArrow, WindStreaks} from '../parts/archery';

// Close on the target: an arrow aimed a little upwind rides the breeze in a gentle curve and lands
// close to the center (not in it), then quivers. It lands on the word "landed" (or the shot's last word).
export const about = "Close-up of an archery target: an arrow curves with the wind and lands close to the center on the word 'landed'.";

const Background: React.FC<DrawContext> = ({t, words}) => {
	const land = wordAt(words, /^land/i) ?? lastWordAt(words, 2);
	return (
		<g>
			<Backdrop t={t} />
			<WindStreaks t={t} gentle />
			<CurvingArrow t={t} land={Math.max(1.4, land)} />
		</g>
	);
};

export const location: Location = {id: 'arrow-lands-close', groundY: 1040, propSlots: [], Background};
