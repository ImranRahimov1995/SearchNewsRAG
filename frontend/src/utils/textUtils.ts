/**
 * @fileoverview Text utility functions for keyword highlighting
 */

/**
 * Highlights specified keywords in text by wrapping them in HTML spans.
 *
 * @param text - The text to search and highlight keywords in
 * @param keywords - Array of keywords to highlight
 * @returns HTML string with highlighted keywords
 *
 * @example
 * highlightKeywords('Hello world', ['world'])
 * // Returns: 'Hello <span class="highlight-keyword">world</span>'
 */
export const highlightKeywords = (text: string, keywords: string[]): string => {
  if (!keywords || keywords.length === 0) return text;

  let highlightedText = text;

  keywords.forEach((keyword) => {
    const regex = new RegExp(`(${keyword})`, 'gi');
    highlightedText = highlightedText.replace(
      regex,
      '<span class="highlight-keyword">$1</span>'
    );
  });

  return highlightedText;
};
