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

    // handle pasting text into text entry field properly (strip formatting)
    $("#text-entry").on("paste", function() {
        var el = $(this);
        setTimeout(function() {
            $("div,p,br", el).after("\n");
            $("span.nlp-highlighted", el).before("HIGHLIGHT000START").after("HIGHLIGHT000END");
            var text = $(el).text();
            text = text.replace(/\n/mgi, "<br>").replace(/HIGHLIGHT000START/mgi, "<span class=\"nlp-highlighted\">")
                       .replace(/HIGHLIGHT000END/mgi, "</span>");
            el.html(text);
        }, 50);
    });

    // analyze text and display results
    $("#analyze-text").click(function() {

        // get rid of active state on the analysis button
        $("#analyze-text").blur();

        // get text
        var text = $("#text-entry").html();
        text = text.replace(/<div[^>]*>/mgi, '\n').replace(/<\/div[^>]*>/mgi, '')
                   .replace(/<span[^>]*>/mgi, '').replace(/<\/span[^>]*>/mgi, '')
                   .replace(/<br[^>]*>/mgi, '').replace(/<\/br[^>]*>/mgi, '');
        console.log(text);

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
                    console.log(result);
                    $("#character-count").text(result.character_count.toString());
                    $("#word-count").text(result.word_count.toString());
                    $("#vocabulary-size").text(result.vocabulary_size.toString());
                    $("#sentence-count").text(result.sentence_count.toString());
                    $("#words-per-sentence").text((Math.round(result.words_per_sentence * 10) / 10).toString());
                    $("#declarative-ratio").text((Math.round(result.declarative_ratio * 1000) / 10).toString() + "%");
                    $("#interrogative-ratio").text((Math.round(result.interrogative_ratio * 1000) / 10).toString() + "%");
                    $("#exclamative-ratio").text((Math.round(result.exclamative_ratio * 1000) / 10).toString() + "%");
                    $("#stopword-ratio").text((Math.round(result.stopword_ratio * 1000) / 10).toString() + "%");
                    $("#syllables-per-word").text((Math.round(result.syllables_per_word * 10) / 10).toString());
                    $("#characters-per-word").text((Math.round(result.characters_per_word * 10) / 10).toString());
                    $("#readability").text((Math.round(result.readability * 10) / 10).toString());
                    $("#noun-ratio").text((Math.round(result.noun_ratio * 1000) / 10).toString() + "%");
                    $("#pronoun-ratio").text((Math.round(result.pronoun_ratio * 1000) / 10).toString() + "%");
                    $("#verb-ratio").text((Math.round(result.verb_ratio * 1000) / 10).toString() + "%");
                    $("#adjective-ratio").text((Math.round(result.adjective_ratio * 1000) / 10).toString() + "%");
                    $("#adverb-ratio").text((Math.round(result.adverb_ratio * 1000) / 10).toString() + "%");
                    $("#determiner-ratio").text((Math.round(result.determiner_ratio * 1000) / 10).toString() + "%");
                    $("#other-pos-ratio").text((Math.round(result.other_pos_ratio * 1000) / 10).toString() + "%");
                    $("#word-freq").html(result.word_freq);
                    $("#bigram-freq").html(result.bigram_freq);
                    $("#trigram-freq").html(result.trigram_freq);
                    $("#results-table").show();
                    $("#analyze-text").button('reset');
                },
                error: function(request, textStatus, error) {
                    alert("Cannot analyze text: " + error);
                }
            });
        };

    });

});
