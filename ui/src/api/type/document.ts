interface DocumentMeta {
    source_url: string;
}

interface Paragraph {
    title: string;
    content: string;
}

interface DocumentSearchData {
    document_id: string;
    document_name: string;
    document_meta: DocumentMeta;
    paragraph_list: Array<Paragraph>;
}

export type { DocumentSearchData }