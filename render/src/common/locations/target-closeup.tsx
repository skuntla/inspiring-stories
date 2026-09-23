import React from 'react';
import type {DrawContext, Location} from '../../kit/types';
import {Backdrop, WindStreaks} from '../parts/archery';

// Close on a straw archery target with red rings, the courtyard soft behind; no arrow. A gentle wind
// moves the corner flag and drifts faint streaks across.
export const about = "Close-up of a straw archery target with red rings, untouched; a gentle wind moves a flag in the corner.";

const Background: React.FC<DrawContext> = ({t}) => (
	<g>
		<Backdrop t={t} />
		<WindStreaks t={t} gentle />
	</g>
);

export const location: Location = {id: 'target-closeup', groundY: 1040, propSlots: [], Background};
