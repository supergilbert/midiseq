#ifndef __MIDIFILE_H
#define __MIDIFILE_H


#include "seqtool/seqtool.h"
#include "midi/midiev.h"

/* #define copy_to_2B(dst, src)	(dst) = *(src);			\ */
/*                                       (dst) = *(src + 1) */

/* #define copy_to_4B(dst, src)	(dst) = *(src);		\ */
/*                                       (dst) = *(src + 1);	\ */
/*                                       (dst) = *(src + 2);	\ */
/*                                       (dst) = *(src + 3)) */

#define get_midifile_type_str(type) ((type) == 0 ?	"Single track"	\
				     : (type) == 1 ?	"Multiple tracks, synchronous" \
				     : (type) == 2 ? "Multiple tracks, asynchronous" \
				     : "Unknown midifile format type")

#define TICK_PER_BEAT 0
#define FRAME_PER_SEC 1
typedef struct
{
  bool_t     flag;              /* True=FPS FALE=TPB (tick per beat) */

  union {
    uint16_t tick_per_beat;
    struct {
      byte_t smpte_frames;
      byte_t ticks_per_frame;
    }        frame_per_sec;
  }          value;

}            midifile_time_division_t;

typedef enum {
  ONETRACK_MIDIFILE = 0,
  MULTITRACK_MIDIFILE_SYNC,
  MULTITRACK_MIDIFILE_USYNC
}			seqtype_t;

typedef struct midifile_hdr_chunk_s
{
  seqtype_t                format_type;
  uint16_t                 number_of_track;
  midifile_time_division_t time_division;
}                          midifile_hdr_chunk_t;

typedef struct
{
  seqtype_t type;
  uint_t    tempo; /* microseconds */
  uint_t    ppq;
  char      *name;
}           midifile_info_t;

typedef struct
{
  /* midifile_hdr_chunk_t  *hdr_info; */
  midifile_info_t       info;
  /* integrer les fonctions de clock au prochaine sequence, compatible au track node*/
  uint_t                number_of_track;
  list_t                track_list;
}                       midifile_t;

#include <unistd.h>
/* #include "seqtool/seqtool.h" */

/* int get_midifile_hdr_chunk(midifile_hdr_chunk_t *mdhdr, void *ptr); */
/* void read_midifile(char *filepath); */
size_t get_midifile_track_size(byte_t *buffer);

bool_t get_midifile_hdr(midifile_hdr_chunk_t *mdhdr, void *ptr);
midifile_t *read_midifile_fd(int fd);
void free_midifile(midifile_t *sequence);

track_t  *midifile_to_onetrack(char *filename);

#endif
