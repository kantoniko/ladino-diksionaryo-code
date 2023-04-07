$(document).ready(function(){

  $(".navbar-burger").click(function() {
      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      $(".navbar-burger").toggleClass("is-active");
      $(".navbar-menu").toggleClass("is-active");
  });

  // Sorting from: https://orangeable.com/javascript/jquery-table-sorting
  $(document).on("click", "table thead tr th:not(.no-sort)", function() {
  	var table = $(this).parents("table");
  	var rows = $(this).parents("table").find("tbody tr").toArray().sort(TableComparer($(this).index()));
  	var dir = ($(this).hasClass("sort-asc")) ? "desc" : "asc";

  	if (dir == "desc") {
  		rows = rows.reverse();
  	}

  	for (var i = 0; i < rows.length; i++) {
  		table.append(rows[i]);
  	}

  	table.find("thead tr th").removeClass("sort-asc").removeClass("sort-desc");
  	$(this).removeClass("sort-asc").removeClass("sort-desc") .addClass("sort-" + dir);
  });

  function TableComparer(index) {
  	return function(a, b) {
  		var val_a = TableCellValue(a, index);
  		var val_b = TableCellValue(b, index);
  		var result = ($.isNumeric(val_a) && $.isNumeric(val_b)) ? val_a - val_b : val_a.toString().localeCompare(val_b);

  		return result;
  	}
  }

  function TableCellValue(row, index) {
  	return $(row).children("td").eq(index).text();
  }
  // end table sort

  function set_local_date() {
      // Assume a date format of "2021-04-13T19:00:00+03:00";
      // Display time in localtime of the browser.
      const dates = document.getElementsByClassName("localdate");
      //console.log(dates);
      //console.log(dates.length);
      for (let ix=0; ix < dates.length; ix++) {
          const mydate = dates[ix].getAttribute("x-schedule");
          const date = new Date(mydate);
          dates[ix].innerHTML = date.toLocaleDateString( [], {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: 'numeric',
              minute: 'numeric',
              timeZoneName: 'long'
          });
      }
  }

    function highlight() {
        //console.log('highlight');
        if (window.location.search.length > 0) {
            const pieces = window.location.search.substring(1).split("=");
            if (pieces[0] == 'highlight') {
                const word = pieces[1];
                //console.log(`highlight ${word}`);
                let match = /^a$/;

                //const term = `a:contains(${word})`;
                // This is nicer, but matches any substring
                //$(term).addClass('has-background-warning');

                // here we check exact match, but that does not hand case insensitive match
                //$(term).each(function() {
                //    if ($(this).html() == word) {
                //        $(this).addClass('has-background-warning');
                //    }
                //});

                // case insenstivie but exact match.
                $('a').each(function() {
                    if ($(this).html().toLowerCase()  == word.toLowerCase() ) {
                        $(this).addClass('has-background-warning');
                    }
                });
            }
        }
    }

  set_local_date();
  highlight();

});
