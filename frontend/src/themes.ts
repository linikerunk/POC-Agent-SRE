/**
 * Temas adicionais para o ChatBot
 * Você pode trocar as cores na App para usar diferentes temas
 */

export const themes = {
  dark: {
    bg: 'from-slate-950 via-slate-900 to-slate-950',
    sidebar: 'from-slate-900 via-slate-950 to-slate-950',
    primary: 'from-blue-600 to-blue-700',
    primaryHover: 'from-blue-500 to-blue-600',
    secondary: 'to-purple-600',
    card: 'bg-slate-800/50',
    border: 'border-slate-700/50',
    text: 'text-slate-100',
    textSecondary: 'text-slate-400',
  },

  ocean: {
    bg: 'from-cyan-950 via-blue-950 to-slate-950',
    sidebar: 'from-cyan-900 via-blue-950 to-slate-950',
    primary: 'from-cyan-600 to-blue-700',
    primaryHover: 'from-cyan-500 to-blue-600',
    secondary: 'to-teal-600',
    card: 'bg-cyan-800/20',
    border: 'border-cyan-700/50',
    text: 'text-cyan-100',
    textSecondary: 'text-cyan-400',
  },

  sunset: {
    bg: 'from-rose-950 via-orange-950 to-amber-950',
    sidebar: 'from-rose-900 via-orange-950 to-amber-950',
    primary: 'from-orange-600 to-red-700',
    primaryHover: 'from-orange-500 to-red-600',
    secondary: 'to-pink-600',
    card: 'bg-orange-800/20',
    border: 'border-orange-700/50',
    text: 'text-orange-100',
    textSecondary: 'text-orange-400',
  },

  forest: {
    bg: 'from-emerald-950 via-green-950 to-slate-950',
    sidebar: 'from-emerald-900 via-green-950 to-slate-950',
    primary: 'from-emerald-600 to-green-700',
    primaryHover: 'from-emerald-500 to-green-600',
    secondary: 'to-lime-600',
    card: 'bg-emerald-800/20',
    border: 'border-emerald-700/50',
    text: 'text-emerald-100',
    textSecondary: 'text-emerald-400',
  },

  purple: {
    bg: 'from-purple-950 via-indigo-950 to-slate-950',
    sidebar: 'from-purple-900 via-indigo-950 to-slate-950',
    primary: 'from-purple-600 to-indigo-700',
    primaryHover: 'from-purple-500 to-indigo-600',
    secondary: 'to-fuchsia-600',
    card: 'bg-purple-800/20',
    border: 'border-purple-700/50',
    text: 'text-purple-100',
    textSecondary: 'text-purple-400',
  },

  neon: {
    bg: 'from-slate-950 via-slate-900 to-slate-950',
    sidebar: 'from-slate-900 via-slate-950 to-slate-950',
    primary: 'from-lime-500 to-cyan-500',
    primaryHover: 'from-lime-400 to-cyan-400',
    secondary: 'to-pink-500',
    card: 'bg-slate-800/50',
    border: 'border-lime-500/30',
    text: 'text-lime-100',
    textSecondary: 'text-lime-400',
  },
};

export type Theme = keyof typeof themes;

/**
 * Exemplo de uso em App.tsx:
 *
 * const [theme, setTheme] = useState<Theme>('dark');
 * const currentTheme = themes[theme];
 *
 * <main className={`bg-gradient-to-b ${currentTheme.bg}`}>
 *   ...
 * </main>
 */
