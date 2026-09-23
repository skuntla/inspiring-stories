import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// The Novice: a young monk of about fifteen; warm tan skin, a clean-shaven head, a bright yellow-orange
// robe with a red sash. The `aim` stance draws his bow.
export const rig: Rig = {
	id: 'novice',
	stances: ['stand', 'walk', 'sit', 'aim'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 470,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#d49a6a',
		skinShade: '#b8805a',
		shaved: '#7a563e',
		brows: '#3a2a20',
		shirt: '#f0b43c',
		shirtShade: '#d39a2a',
		sleeves: 'long',
		pants: '#f0b43c',
		shoes: '#8a5a2e',
		robe: {sash: '#b8322e'},
	}),
};
