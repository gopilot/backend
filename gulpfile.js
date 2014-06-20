var gulp = require('gulp');
var stylus = require('gulp-stylus');
var nib = require('nib');
var rupture = require('rupture');

// compile css
gulp.task('stylus', function () {
  gulp.src('./stylus/master.styl')
    .pipe(stylus({errors: true, use: [nib(), rupture()]}))
    .pipe(gulp.dest('./app/static'));
});


gulp.task('default', ['stylus'], function(){
});

gulp.task('watch', function() {
  gulp.watch('stylus/*.styl', ['stylus']);
});
