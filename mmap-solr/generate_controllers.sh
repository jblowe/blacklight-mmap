

paste mmap-sites.fields.txt mmap-sites.fields.txt | perl -pe "s/^/   ('/;s/\t/', '/;s/$/'),/;s/_s//;s/_/ /;" > config-mmap-sites.py
paste mmap-sites.fields.txt mmap-sites.fields.txt | perl -pe "s/_/ /;s/^/   config.add_index_field '/;s/\t/', label: '/;s/_s//;s/$/'/" > controller.rb
perl -pe 's/_index_/_show_/' controller.rb > show.rb
perl -pe 's/_index_/_facet_/;s/$/, limit: true/' controller.rb > facet.rb
cp controller.rb index.rb
cat  facet.rb index.rb show.rb > ctrl.rb

