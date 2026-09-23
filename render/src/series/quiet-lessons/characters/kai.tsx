import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Kai: a sincere young monk; light brown skin, a clean-shaven head, a saffron robe with a maroon
// sash over one shoulder. The `aim` stance draws his bow.
export const rig: Rig = {
	id: 'kai',
	stances: ['stand', 'walk', 'sit', 'aim'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 470,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#c98c62',
		skinShade: '#ad7550',
		shaved: '#6b4a36',
		brows: '#2c211c',
		shirt: '#e39a3b',
		shirtShade: '#c47d26',
		sleeves: 'long',
		pants: '#e39a3b',
		shoes: '#8a5a2e',
		robe: {sash: '#7a2e2a'},
	}),
};
