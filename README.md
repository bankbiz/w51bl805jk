# w51bl805jk


aws s3 cp label_images/ s3://graffity-public-assets/ronn-temp/label_images/ --acl public-read --recursive

aws s3 sync . s3://graffity-public-assets/ronn-temp/label_images/ --acl public-read