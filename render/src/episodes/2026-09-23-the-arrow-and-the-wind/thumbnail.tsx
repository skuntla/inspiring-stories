import React from 'react';
import {WindMissEmblem} from '../../common/parts/archery';
import {rig as kai} from '../../series/quiet-lessons/characters/kai';
import {rig as ren} from '../../series/quiet-lessons/characters/master-ren';
import {location as courtyard} from '../../series/quiet-lessons/locations/monastery-courtyard';
import type {ThumbnailSpec} from '../../thumbnail/Thumbnail';

// Frustrated Kai (left) and a smiling Master Ren pointing (right) across the story's problem: an arrow
// bent away from the target by the wind.
export const thumbnail: ThumbnailSpec = {
	background: courtyard,
	view: [760, 560, 1.3], // keeps the courtyard's own target out of frame; the flag shows the wind
	timeOfDay: 'morning',
	characters: [
		{rig: kai, stance: 'stand', mood: 'worried', facing: 'right', x: 330, ground: 1330, scale: 1.75},
		{rig: ren, stance: 'reach', mood: 'happy', facing: 'left', x: 1610, ground: 1330, scale: 1.7},
	],
	Center: () => (
		<g transform="translate(990 650) scale(0.95)">
			<WindMissEmblem />
		</g>
	),
	headlines: ['WHY YOU KEEP *MISSING*\n*YOUR TARGET*', 'STOP *FORCING* IT', 'YOUR HARD WORK\nIS *NOT WASTED*'],
};
