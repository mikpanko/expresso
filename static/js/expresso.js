var text = null;
var tokens = null;
var metrics = null;

$(function(){

    // run at start
    $(document).ready(function() {

        // set navigation bar
        $(".navbar-all").removeClass("active");

        // hide results table
        $("#results-table").hide();

        //
        $("div[data-placeholder]").on("input", function() {
            var el = $(this);
            console.log(el.text().length);
		    if (el.text().length) {
			    el.removeClass("data-text-empty");
                el.addClass("data-text-filled");
		    }
		    else {
                el.removeClass("data-text-filled");
			    el.addClass("data-text-empty");
                el.html("");
		    }
	});

    });

    // get rid of active state on the mobile menu button
    $(".navbar-toggle").click(function() {
        $(".navbar-toggle").blur();
    });

    // strip formatting pasting text into text entry field
    $("#text-entry").on("paste", function() {
        var el = $(this);
        setTimeout(function() {
            el.html(cleanHtml(el.html()));
        }, 10);
    });

    // reset text, tokens, and metrics when text is changed
    $("#text-entry").on("input", function() {
        text = null;
        tokens = null;
        metrics = null;
    });

    // analyze text and display results
    $("#analyze-text").click(function() {

        // get rid of active state on the analysis button
        $("#analyze-text").blur();

        // get text
        text = html2text($("#text-entry").html());

        if (text) {

            // put UI in analyzing mode
            $("#analyze-text").button('loading');
            $("#results-table").hide();

            // send text to the server
            $.ajax({
                type: "POST",
                url: "/analyze-text",
                dataType: "json",
                data: {
                    text: text
                },
                success: function(result, textStatus, error) {

                    // display analysis results
                    tokens = result.tokens;
                    metrics = result.metrics;
                    $("#character-count").text(metrics.character_count.toString());
                    $("#word-count").text(metrics.word_count.toString());
                    $("#vocabulary-size").text(metrics.vocabulary_size.toString());
                    $("#sentence-count").text(metrics.sentence_count.toString());
                    $("#words-per-sentence").text((Math.round(metrics.words_per_sentence * 10) / 10).toString());
                    $("#declarative-ratio").text((Math.round(metrics.declarative_ratio * 1000) / 10).toString() + "%");
                    $("#interrogative-ratio").text((Math.round(metrics.interrogative_ratio * 1000) / 10).toString() + "%");
                    $("#exclamative-ratio").text((Math.round(metrics.exclamative_ratio * 1000) / 10).toString() + "%");
                    $("#stopword-ratio").text((Math.round(metrics.stopword_ratio * 1000) / 10).toString() + "%");
                    $("#syllables-per-word").text((Math.round(metrics.syllables_per_word * 10) / 10).toString());
                    $("#characters-per-word").text((Math.round(metrics.characters_per_word * 10) / 10).toString());
                    $("#readability").text((Math.round(metrics.readability * 10) / 10).toString());
                    $("#noun-ratio").text((Math.round(metrics.noun_ratio * 1000) / 10).toString() + "%");
                    $("#pronoun-ratio").text((Math.round(metrics.pronoun_ratio * 1000) / 10).toString() + "%");
                    $("#verb-ratio").text((Math.round(metrics.verb_ratio * 1000) / 10).toString() + "%");
                    $("#adjective-ratio").text((Math.round(metrics.adjective_ratio * 1000) / 10).toString() + "%");
                    $("#adverb-ratio").text((Math.round(metrics.adverb_ratio * 1000) / 10).toString() + "%");
                    $("#determiner-ratio").text((Math.round(metrics.determiner_ratio * 1000) / 10).toString() + "%");
                    $("#other-pos-ratio").text((Math.round(metrics.other_pos_ratio * 1000) / 10).toString() + "%");
                    $("#word-freq").html(metrics.word_freq);
                    $("#bigram-freq").html(metrics.bigram_freq);
                    $("#trigram-freq").html(metrics.trigram_freq);
                    $("#results-table").show();
                    $("#analyze-text").button('reset');

                },
                error: function(request, textStatus, error) {
                    alert("Cannot analyze text: " + error);
                }
            });
        };

    });

    // convert html to text
    function html2text(htmlStr) {
        htmlStr = htmlStr.replace(/<div><br><\/div>/mgi, "");
        var el = $("<div>").html(htmlStr);
        $("div,p,br", el).after("\n");
        return el.text().trim();
    }

    // clean html of formatting
    function cleanHtml(htmlStr) {
        var el = $("<div>").html(htmlStr);
        $("div,p,br", el).after("\n");
        $("span.nlp-highlighted", el).before("HIGHLIGHT000START").after("HIGHLIGHT000END");
        return el.text().trim().replace(/\n/mgi, "<br>").replace(/HIGHLIGHT000START/mgi, "<span class=\"nlp-highlighted\">")
            .replace(/HIGHLIGHT000END/mgi, "</span>");
    }

    window.html2text = html2text;
    window.cleanHtml = cleanHtml;

});
