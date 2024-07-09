SELECT
    "document".name as document_name,
    "document"."meta" as document_meta,
	"paragraph".*
FROM
	"paragraph" "paragraph" left join "document" "document" on  "paragraph".document_id = "document"."id"
