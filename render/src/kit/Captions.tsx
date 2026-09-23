import React from 'react';
import type {CaptionPage} from './types';

/** Word-level captions: the current page, the spoken word highlighted, a label for dialogue. */
export const Captions: React.FC<{pages: CaptionPage[]; frame: number}> = ({pages, frame}) => {
	const page = pages.find((p) => frame >= p.from && frame < p.to);
	if (!page) return null;
	return (
		<div style={{position: 'absolute', bottom: 44, width: '100%', display: 'flex', justifyContent: 'center'}}>
			<div
				style={{
					background: 'rgba(36, 30, 22, 0.58)',
					borderRadius: 18,
					padding: '12px 30px 14px',
					maxWidth: '82%',
					textAlign: 'center',
					fontFamily: 'Georgia, "Times New Roman", serif',
					fontStyle: page.speaker ? 'normal' : 'italic',
					fontSize: 50,
					lineHeight: 1.25,
					color: '#f7f1e4',
				}}
			>
				{page.speaker && (
					<div style={{fontFamily: 'system-ui, sans-serif', fontStyle: 'normal', fontWeight: 700, fontSize: 22,
						letterSpacing: 4, textTransform: 'uppercase', color: '#f3a54f'}}>
						{page.speaker}
					</div>
				)}
				{page.words.map(([text, from, to], i) => (
					<span key={i} style={{color: frame >= from && frame < to ? '#ffd98a' : '#f7f1e4'}}>
						{text}
						{i < page.words.length - 1 ? ' ' : ''}
					</span>
				))}
			</div>
		</div>
	);
};
