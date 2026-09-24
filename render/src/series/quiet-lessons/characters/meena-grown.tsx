import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// Meena, grown (about thirty): hair in a bun, a red bindi, a mustard sari over a red blouse, the
// sari's pallu over one shoulder. Keeps the well's records.
export const rig: Rig = {
	id: 'meena-grown',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 465,
	anchors: {hand: [90, -262], head: [8, -482]},
	Component: makeHuman({
		skin: '#a86f48', skinShade: '#8c5a3a',
		hair: {color: '#1f1814', style: 'bun'}, brows: '#1f1814', bindi: '#c8323a',
		shirt: '#b8322e', shirtShade: '#962824', sleeves: 'rolled',
		skirt: {color: '#e0a33a', shade: '#c4862a', hem: -40}, robe: {sash: '#e8b04a'},
		pants: '#a86f48', shoes: '#8a5a2e',
	}),
};
