import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// A wandering traveller who sees Velu return the coin: a grey beard, a brown head wrap, a sand-coloured
// long kurta and a brown shawl over one shoulder.
export const rig: Rig = {
	id: 'traveller',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 490,
	anchors: {hand: [90, -262], head: [8, -522]},
	Component: makeHuman({
		skin: '#b07a52', skinShade: '#94643f',
		turban: {color: '#8a6a4a', shade: '#6e543a'}, beard: '#9a948a', brows: '#9a948a', browWidth: 5,
		shirt: '#d9c9a8', shirtShade: '#bfae8a', sleeves: 'long',
		skirt: {color: '#d9c9a8', shade: '#bfae8a', hem: -70}, robe: {sash: '#8a6a4a'},
		pants: '#b9a888', shoes: '#6b4a2e', stoop: 3,
	}),
};
