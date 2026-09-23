import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Arjun: early 40s, warm brown skin, short black hair greying at the temples, light stubble,
// teal shirt with rolled sleeves (his signature), charcoal trousers, brown shoes.
export const rig: Rig = {
	id: 'arjun',
	stances: ['stand', 'walk', 'sit', 'hold', 'reach'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 470,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#b97a56',
		skinShade: '#9c6444',
		hair: {color: '#2b2320', greyTemples: '#a39c94'},
		stubble: true,
		brows: '#2b2320',
		shirt: '#3f7f86',
		shirtShade: '#2f6168',
		sleeves: 'rolled',
		pants: '#4a4d55',
		shoes: '#6b4a32',
	}),
};
