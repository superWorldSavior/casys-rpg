export interface Book {
  id: string;
  title: string;
  author: string;
  filename: string;
  uploadDate: string;
  status: string;
  current_page?: number;
  total_pages?: number;
  processed_sections?: number;
  processed_images?: number;
  error_message?: string;
  cover_image?: string;
}

export interface BookSection {
  id: string;
  content: string;
}

export interface BookMetadata {
  sections: BookSection[];
  title: string;
  total_sections: number;
}
