// One codebase, two releases. Every `NEW ? ... : ...` below is a change shipped in 5.40.
export const RELEASE = import.meta.env.VITE_RELEASE || '5.40'
export const NEW = RELEASE === '5.40'
