/// <reference types="vite/client" />

declare module "*.png" {
  const src: string;
  export default src;
}

declare module "*.svg" {
  const src: string;
  export default src;
}

declare module "*.jpeg" {
  const src: string;
  export default src;
}

declare module "*.jpg" {
  const src: string;
  export default src;
}

declare module "*.asset.json" {
  const content: {
    version: number;
    asset_id: string;
    project_id: string;
    url: string;
    r2_key?: string;
    original_filename: string;
    size?: number;
    content_type?: string;
    created_at?: string;
  };
  export default content;
}
