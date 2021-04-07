$(window).load(function () {

	/* Gestione della tastiera virtuale su dispositivi mobili che occultano lo show dei campi di input */
	var $FixedSmall = $('.FixedSmall');
	$('.Form-input').focusin(function() {
	  $FixedSmall.addClass('off');
	});
	$('.Form-input').focusout(function() {
	  $FixedSmall.removeClass('off');
	});

	/* INDEX PAGE */
	$('.Button--welcome, .Button--welcome-close').on('click', function(e) {
		e.preventDefault();
		var showtarget = $(this).data('showtarget');
		var $showtarget = $(showtarget);
		var $body = $('body');
		var $buttonwelcome = $('.Button--welcome');
		var $spidanimation = $('#spid-animation');
		var $mainheader = $('#main-header');
		var $mainheader_left = $mainheader.find('.fadeInLeft');
		var $mainheader_right = $mainheader.find('.fadeInRight');
		var $showtarget_in = $showtarget.find('.Providersgrid-item');
		var $showtarget_inup = $showtarget.find('h1');
		var $showtarget_form = $('form');
		var $showtarget_footer = $('#non-hai-spid');
		
		if ($showtarget.hasClass('shown')) {
			//$buttonwelcome.fadeIn('fast');
			//$showtarget.hide();
			//$showtarget.removeClass('shown');
			$body.addClass('blockScroll');
			$mainheader_left.addClass('fadeOutLeft');
			$mainheader_right.addClass('fadeOutRight');
			$showtarget_inup.each(function() {
				$(this).removeClass('fadeInUp');
				$(this).addClass('fadeOutDown');
			});
			$showtarget_in.each(function() {
				$(this).removeClass('fadeIn');
				$(this).addClass('fadeOut');
			});
			$showtarget_form.removeClass('fadeIn');
			$showtarget_form.addClass('fadeOut');
			$showtarget_footer.removeClass('fadeIn');
			$showtarget_footer.addClass('fadeOut');

			$showtarget.removeClass('shown');
			$spidanimation.removeClass('runAnimation');
			$spidanimation.addClass('runBackAnimation');
			$buttonwelcome.fadeTo(1500,1).fadeIn(300);
			
			
		} else {
			$buttonwelcome.fadeOut('fast');
			$spidanimation.removeClass('runBackAnimation');
			$spidanimation.addClass('runAnimation');
			$mainheader.css('visibility','visible');
			$mainheader_left.removeClass('fadeOutLeft');
			$mainheader_right.removeClass('fadeOutRight');
			$showtarget.show();
			$showtarget_inup.each(function() {
				$(this).removeClass('fadeOutDown');
				$(this).addClass('fadeInUp');
			});
			$showtarget_in.each(function() {
				$(this).removeClass('fadeOut');
				$(this).addClass('fadeIn');
			});
			$showtarget_form.removeClass('fadeOut');
			$showtarget_form.addClass('fadeIn');
			$showtarget_footer.removeClass('fadeOut');
			$showtarget_footer.addClass('fadeIn');

			$showtarget.addClass('shown');
			$body.removeClass('blockScroll');
		}


	});

	/* validatore minimo per form */
	function minValidator($inputs) {

		var allValid = true;

		$inputs.each(function() {
	        var elem = $(this)[0];
	        var $elem = $(this);
	        if (typeof elem.willValidate !== "undefined") {
	            if (elem.checkValidity()==true) {
	                $elem.removeClass('error');
	                allValid = allValid==false ? false : true;
	            } else {
	                $elem.addClass('error');
	                allValid = allValid==true ? false : false;
	            }
	        } else {
	        	return allValid;
	        }
	    });

		return allValid;

	}

	/* Listner click al submit utile per intercettare vampi non validi e mostrare icone */
	$('form button[type="submit"][name="confirm"]').on('click',function(event) {
	    var $inputs = $('.Form-input');

	    minValidator($inputs);
	    
	});
	

	/* Listner click al submit utile per intercettare vampi non validi e mostrare icone */
	$('form button[type="submit"][name="delete"]').on('click',function(event) {
		$('.Form-input').prop('required', false);
	});

	/* Listner all'uscita dal campo di input per gestire il disabling del bottone submit */
	$('.Form-input').on('focusout, input', function() {
	  var $inputs = $('.Form-input');
	  var $cta = $('form button.js-cta');
	  minValidator($inputs) ? $cta.removeAttr('disabled') : $cta.attr('disabled', 'disabled');
	});

	/* Animazione input */
	$(function() {
		var formAnimatedInput = $('.form-animate-fields .Form-input');

		formAnimatedInput.each(function() {
		var $this = $(this);

		$this.on('focus', function() {
		  $this.addClass('is-filled');
		});

		$this.on('blur', function() {
		  if($this.val().length == 0) {
		    $this.removeClass('is-filled');
		  }
		});
	});
	});
});

