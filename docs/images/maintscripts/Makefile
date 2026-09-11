ALL_GRAPHS := $(wildcard *.dot)
SVG_IMAGES := $(ALL_GRAPHS:%.dot=%.svg)
PDF_IMAGES := $(SVG_IMAGES:%.svg=%.pdf)

all: $(SVG_IMAGES) $(PDF_IMAGES)

clean:
	rm -f $(SVG_IMAGES) $(PDF_IMAGES)

%.svg: %.dot
	dot -T svg -o $@ $<

%.pdf: %.svg
	inkscape --export-type pdf -o $@ $<
