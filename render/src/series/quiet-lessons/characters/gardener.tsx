import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// The Gardener: elderly, deep brown skin, full white beard and bushy white brows, slightly stooped,
// a wide straw hat (his signature), cream kurta and a leaf-green apron.
export const rig: Rig = {
	id: 'gardener',
	stances: ['stand', 'walk', 'hold', 'reach'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 460,
	anchors: {hand: [90, -262], head: [8, -524]},
	Component: makeHuman({
		skin: '#a8704c',
		skinShade: '#8c5a3a',
		beard: '#f1ede4',
		brows: '#f1ede4',
		browWidth: 7,
		shirt: '#efe6d2',
		shirtShade: '#d8ccb2',
		sleeves: 'long',
		pants: '#e2d7bf',
		shoes: '#7a5234',
		apron: '#6d8b4a',
		hat: {brim: '#d9b25c', crown: '#cfa64e', band: '#8a5a2e'},
		stoop: 5,
	}),
};
