import type { StructureResolver } from 'sanity/structure';

export const deskStructure: StructureResolver = (S) =>
  S.list()
    .title('Content')
    .items([
      S.listItem()
        .title('Site')
        .child(
          S.list()
            .title('Site')
            .items([
              S.listItem()
                .title('Site settings')
                .child(S.document().schemaType('siteSettings').documentId('siteSettings')),
              S.documentTypeListItem('page').title('Pages'),
            ])
        ),
      S.divider(),
      S.listItem()
        .title('Products')
        .child(
          S.list()
            .title('Products')
            .items([
              S.documentTypeListItem('productFamily').title('Product families'),
              S.documentTypeListItem('product').title('Products'),
              S.documentTypeListItem('download').title('Downloads'),
            ])
        ),
      S.documentTypeListItem('industry').title('Industries'),
      S.documentTypeListItem('service').title('Services'),
      S.listItem()
        .title('Proof')
        .child(
          S.list()
            .title('Proof')
            .items([
              S.documentTypeListItem('customer').title('Customers'),
              S.documentTypeListItem('caseStudy').title('Case studies'),
            ])
        ),
      S.divider(),
      S.listItem()
        .title('Journal')
        .child(
          S.list()
            .title('Journal')
            .items([
              S.documentTypeListItem('article').title('Articles'),
              S.documentTypeListItem('author').title('Authors'),
              S.documentTypeListItem('pillar').title('Pillars'),
              S.documentTypeListItem('tag').title('Tags'),
            ])
        ),
    ]);
