import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Master Kai: Kai years later, now a teacher. Same face and skin as Kai, but a deep maroon teacher's
// robe with a saffron sash (like Master Ren's), so the change of role reads at a glance.
export const rig: Rig = {
	id: 'master-kai',
	stances: ['stand', 'walk', 'sit', 'aim'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 470,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#c98c62',
		skinShade: '#ad7550',
		shaved: '#6b4a36',
		stubble: true,
		brows: '#2c211c',
		shirt: '#7a2e2a',
		shirtShade: '#5e211e',
		sleeves: 'long',
		pants: '#7a2e2a',
		shoes: '#6b4a2e',
		robe: {sash: '#e39a3b'},
	}),
};
