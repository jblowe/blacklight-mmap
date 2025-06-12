module ApplicationHelper

  def render_image_link options = {}
    # return a link to an image
    content_tag(:div) do
      options[:value].collect do |filename|
        filename = filename.gsub('#', '%23')
        content_tag(:a, 'location of original photo',
          href: "#{filename}",
          style: 'padding: 3px;',
          class: 'hrefclass')
      end.join.html_safe
    end
  end

  def render_image_link2 options = {}
    # return a link to an image
    content_tag(:div) do
      options[:value].collect do |filename|
        content_tag(:a, 'filename',
          href: "/?q=#{filename}&search_field=FILENAME_ss",
          style: 'padding: 3px;',
          class: 'hrefclass')
      end.join.html_safe
    end
  end

def render_images(options = {})
  # Return a bunch of <img> elements
  cards = options[:value].collect do |imagename|
    content_tag(:div, class: 'card', style: 'width: 18rem; float: left;') do
      image_tag = content_tag(:img, '', src: imagename, class: 'card-img-top')
      card_body = content_tag(:div, class: 'card-body') do
        content_tag(:p, imagename.gsub(/\/images\/.*?\//,'').gsub('.thumb.jpg',''), class: 'card-text')
      end
      image_tag + card_body
    end
  end
  cards.join.html_safe
end

def render_records(options = {})
  # Render the array of subrecords as a table
  content_tag(:table, class: 'table table-sm table-bordered') do
    # nb: this list of fields does NOT include IMAGENAME
    fields = 'DTYPE T SITE YEAR OP SQ LOT ROLL EXP AREA TRAY LEVEL MATERIAL NOTES STRATUM CLASS IMAGENAME FILENAME'.split
    columns = 12
    # Generate the table header
    thead = content_tag(:thead) do
      content_tag(:tr) do
        fields.slice(0, columns).collect do |f|
          content_tag(:th, f)
        end.join.html_safe
      end
    end

    # Generate the table body
    tbody = content_tag(:tbody) do
      options[:value].collect do |sub_records|
        content_tag(:tr) do
          sub_records.split('%').slice(0, columns).map do |x|
            content_tag(:td, x)
          end.join.html_safe
        end
      end.join.html_safe
    end

    # Combine the header and body to form the complete table
    thead + tbody
  end
end

def render_filenames(options = {})
  # Render the array of subrecords as a table
  content_tag(:table, class: 'table table-sm table-bordered') do
    # Generate the table header
    thead = content_tag(:thead) do
      content_tag(:tr) do
        content_tag(:th, 'FILENAMES')
      end
    end

    # Generate the table body
    tbody = content_tag(:tbody) do
      options[:value].collect do |filename|
        content_tag(:tr) do
          content_tag(:td, filename)
        end
      end.join.html_safe
    end

    tbody
  end
end

end
