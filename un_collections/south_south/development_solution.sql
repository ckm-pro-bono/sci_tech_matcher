/*
    The series, Sharing Innovative Experiences, is one of the tools
    to support quality documentation of Southern development experiences.
    Each volume of the series focuses on quality solutions provided
    by developing countries for a related area of development challenges.
    The production of the series engages institutional partners specialized
    in the thematic area for sourcing, selecting, peer reviewing and publishing
    the case studies from practitioners that actually carried out the work.

    http://www.esupp.unsouthsouth.org/gssd-academy-solutions/
*/


CREATE TABLE IF NOT EXISTS development_solution(
    meta_organization TEXT NOT NULL,
    meta_category TEXT NOT NULL,
    meta_collected_date TEXT NOT NULL,
    meta_base_url TEXT NOT NULL,
    volume_title TEXT NOT NULL,
    volume_num INTEGER,
    chapter_title TEXT NOT NULL,
    chapter_num INTEGER,
    country TEXT NOT NULL,
    thematic_area TEXT NOT NULL,
    mdg TEXT NOT NULL,
    abstract TEXT NOT NULL,
    document_url TEXT NOT NULL
);