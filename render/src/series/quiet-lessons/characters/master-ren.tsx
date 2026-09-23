import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Master Ren: an old monk; deep brown skin, a shaven head, a short white beard and white brows,
// slightly stooped, a deep maroon robe with a saffron sash. The `aim` stance draws his bow.
export const rig: Rig = {
	id: 'master-ren',
	stances: ['stand', 'walk', 'sit', 'aim'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 465,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#9a6443',
		skinShade: '#7e4f33',
		shaved: '#5a3a28',
		beard: '#f1ede4',
		brows: '#f1ede4',
		browWidth: 7,
		shirt: '#7a2e2a',
		shirtShade: '#5e211e',
		sleeves: 'long',
		pants: '#7a2e2a',
		shoes: '#6b4a2e',
		robe: {sash: '#e39a3b'},
		stoop: 4,
	}),
};
